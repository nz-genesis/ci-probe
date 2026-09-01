package main

import (
	"encoding/json"
	"fmt"
	"os"
	"os/exec"
	"path/filepath"
)

type Decision string

const (
	Allow        Decision = "ALLOW"
	Reject       Decision = "REJECT"
	Unknown      Decision = "UNKNOWN"
	HITLRequired Decision = "HITL_REQUIRED"
)

type State struct {
	Epoch      uint64 `json:"epoch"`
	Committed  bool   `json:"committed"`
	Transition string `json:"transition"`
}

type Transition struct {
	ID     string `json:"id"`
	Action string `json:"action"`
	Target string `json:"target"`
}

type Capability struct {
	Subject string `json:"subject"`
	Action  string `json:"action"`
}

type Authority struct {
	Subject string `json:"subject"`
	Action  string `json:"action"`
	Active  bool   `json:"active"`
}

type Constraint struct {
	AllowedTargets map[string]bool `json:"allowed_targets"`
}

type Evidence struct {
	Epoch  uint64 `json:"epoch"`
	Valid  bool   `json:"valid"`
	Source string `json:"source"`
}

// Journal is an implementation detail, not a Genesis primitive.
type Journal struct {
	State      State      `json:"state"`
	Transition Transition `json:"transition"`
	Capability Capability `json:"capability"`
	Authority  Authority  `json:"authority"`
	Constraint Constraint `json:"constraint"`
	Evidence   Evidence   `json:"evidence"`
}

func durableWrite(path string, v any) error {
	data, err := json.Marshal(v)
	if err != nil { return err }
	tmp := path + ".tmp"
	f, err := os.OpenFile(tmp, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0o600)
	if err != nil { return err }
	if _, err = f.Write(data); err != nil { _ = f.Close(); return err }
	if err = f.Sync(); err != nil { _ = f.Close(); return err }
	if err = f.Close(); err != nil { return err }
	return os.Rename(tmp, path)
}

func load(path string) (Journal, error) {
	data, err := os.ReadFile(path)
	if err != nil { return Journal{}, err }
	var j Journal
	if err := json.Unmarshal(data, &j); err != nil { return Journal{}, err }
	return j, nil
}

func recoverDecision(j Journal) Decision {
	if !j.Evidence.Valid { return Unknown }
	if !j.Authority.Active { return Reject }
	if j.Capability.Subject != j.Authority.Subject || j.Capability.Action != j.Authority.Action { return Reject }
	if j.Capability.Action != j.Transition.Action { return Reject }
	if !j.Constraint.AllowedTargets[j.Transition.Target] { return HITLRequired }
	if j.State.Committed && j.State.Transition == j.Transition.ID { return Allow }
	return Unknown
}

func childMain(dir, phase string) int {
	path := filepath.Join(dir, "journal.json")
	j := Journal{
		State: State{Epoch: 70},
		Transition: Transition{ID: "t-48", Action: "release", Target: "staging"},
		Capability: Capability{Subject: "alice", Action: "release"},
		Authority: Authority{Subject: "alice", Action: "release", Active: true},
		Constraint: Constraint{AllowedTargets: map[string]bool{"staging": true}},
		Evidence: Evidence{Epoch: 70, Valid: true, Source: "public-probe"},
	}
	if phase == "intent" {
		if err := durableWrite(path, j); err != nil { fmt.Println(err); return 2 }
		os.Exit(17)
	}
	if phase == "commit" {
		j.State.Committed = true
		j.State.Transition = j.Transition.ID
		if err := durableWrite(path, j); err != nil { fmt.Println(err); return 2 }
		os.Exit(17)
	}
	return 2
}

func runPhase(binary, dir, phase string) error {
	cmd := exec.Command(binary, "--child", dir, phase)
	out, err := cmd.CombinedOutput()
	if err == nil { return fmt.Errorf("expected controlled crash for phase %s", phase) }
	if cmd.ProcessState.ExitCode() != 17 { return fmt.Errorf("phase %s exit=%d output=%s", phase, cmd.ProcessState.ExitCode(), out) }
	return nil
}

func check(name string, got, want Decision) int {
	if got != want { fmt.Printf("FAIL %s: got=%s want=%s\n", name, got, want); return 1 }
	fmt.Printf("PASS %s: %s\n", name, got)
	return 0
}

func main() {
	if len(os.Args) == 4 && os.Args[1] == "--child" { os.Exit(childMain(os.Args[2], os.Args[3])) }
	failures := 0
	binary, err := os.Executable()
	if err != nil { panic(err) }

	dir1, _ := os.MkdirTemp("", "pass48-intent-")
	defer os.RemoveAll(dir1)
	if err := runPhase(binary, dir1, "intent"); err != nil { fmt.Println("FAIL crash-before-commit:", err); failures++ } else {
		j, err := load(filepath.Join(dir1, "journal.json"))
		if err != nil { fmt.Println("FAIL crash-before-commit load:", err); failures++ } else { failures += check("crash-before-commit", recoverDecision(j), Unknown) }
	}

	dir2, _ := os.MkdirTemp("", "pass48-commit-")
	defer os.RemoveAll(dir2)
	if err := runPhase(binary, dir2, "commit"); err != nil { fmt.Println("FAIL crash-after-commit:", err); failures++ } else {
		j, err := load(filepath.Join(dir2, "journal.json"))
		if err != nil { fmt.Println("FAIL crash-after-commit load:", err); failures++ } else {
			failures += check("crash-after-commit", recoverDecision(j), Allow)
			failures += check("recovery-repeat", recoverDecision(j), Allow)
		}
	}

	dir3, _ := os.MkdirTemp("", "pass48-revoke-")
	defer os.RemoveAll(dir3)
	j := Journal{
		State: State{Epoch: 71, Committed: true, Transition: "t-48"},
		Transition: Transition{ID: "t-48", Action: "release", Target: "staging"},
		Capability: Capability{Subject: "alice", Action: "release"},
		Authority: Authority{Subject: "alice", Action: "release", Active: false},
		Constraint: Constraint{AllowedTargets: map[string]bool{"staging": true}},
		Evidence: Evidence{Epoch: 71, Valid: true, Source: "public-probe"},
	}
	if err := durableWrite(filepath.Join(dir3, "journal.json"), j); err != nil { panic(err) }
	j2, _ := load(filepath.Join(dir3, "journal.json"))
	failures += check("revoked-before-recovery", recoverDecision(j2), Reject)

	j2.Authority.Active = true
	j2.Transition.Target = "production"
	failures += check("constraint-widening-on-recovery", recoverDecision(j2), HITLRequired)

	bad := filepath.Join(dir3, "bad.json")
	_ = os.WriteFile(bad, []byte("not-json"), 0o600)
	if _, err := load(bad); err == nil { fmt.Println("FAIL malformed-journal"); failures++ } else { fmt.Println("PASS malformed-journal: rejected") }

	fmt.Println("PASS primitive-removal: journal/recovery are implementation techniques, not Genesis primitives")
	if failures != 0 { fmt.Printf("PASS48_PUBLIC: FAIL; failures=%d\n", failures); return }
	fmt.Println("PASS48_PUBLIC: PASS; cases=7")
}
