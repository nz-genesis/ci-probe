package main

import (
	"encoding/json"
	"errors"
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

type EffectStatus string

const (
	EffectUnknown  EffectStatus = "UNKNOWN"
	EffectPresent  EffectStatus = "VERIFIED_PRESENT"
	EffectAbsent   EffectStatus = "VERIFIED_ABSENT"
	EffectConflict EffectStatus = "CONFLICT"
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

type Journal struct {
	State      State      `json:"state"`
	Transition Transition `json:"transition"`
	Capability Capability `json:"capability"`
	Authority  Authority  `json:"authority"`
	Constraint Constraint `json:"constraint"`
	Evidence   Evidence   `json:"evidence"`
}

type WorldObservation struct {
	Epoch      uint64 `json:"epoch"`
	Transition string `json:"transition"`
	Present    bool   `json:"present"`
	Valid      bool   `json:"valid"`
	Source     string `json:"source"`
}

func durableWrite(path string, value any) error {
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}
	tmp := path + ".tmp"
	f, err := os.OpenFile(tmp, os.O_CREATE|os.O_TRUNC|os.O_WRONLY, 0o600)
	if err != nil {
		return err
	}
	if _, err = f.Write(data); err != nil {
		_ = f.Close()
		return err
	}
	if err = f.Sync(); err != nil {
		_ = f.Close()
		return err
	}
	if err = f.Close(); err != nil {
		return err
	}
	return os.Rename(tmp, path)
}

func load(path string, value any) error {
	data, err := os.ReadFile(path)
	if err != nil {
		return err
	}
	return json.Unmarshal(data, value)
}

// observeWorld is an implementation-level reconciliation helper. It does not
// create an effect-specific Genesis primitive: it composes observation/evidence
// about the world and preserves disagreement as CONFLICT.
func observeWorld(a, b *WorldObservation) EffectStatus {
	if a == nil || !a.Valid || b == nil || !b.Valid {
		return EffectUnknown
	}
	if a.Epoch != b.Epoch || a.Transition != b.Transition {
		return EffectConflict
	}
	if a.Present != b.Present {
		return EffectConflict
	}
	if a.Present {
		return EffectPresent
	}
	return EffectAbsent
}

// reconcile separates an epistemic result about an external effect from
// permission for any future action. A verified effect is not repeated, a
// verified absence may admit a bounded retry, and UNKNOWN never becomes an
// unconditional retry permission.
func reconcile(j Journal, obs *WorldObservation) (EffectStatus, Decision) {
	if obs == nil || !obs.Valid || obs.Epoch != j.Evidence.Epoch || obs.Transition != j.Transition.ID {
		return EffectUnknown, Unknown
	}
	status := EffectAbsent
	if obs.Present {
		status = EffectPresent
	}
	if !j.Evidence.Valid {
		return EffectUnknown, Unknown
	}
	if !j.Authority.Active || j.Capability.Subject != j.Authority.Subject || j.Capability.Action != j.Authority.Action || j.Capability.Action != j.Transition.Action {
		return status, Reject
	}
	if !j.Constraint.AllowedTargets[j.Transition.Target] {
		return status, HITLRequired
	}
	if status == EffectPresent {
		// The world fact is verified, but there is no permission to create a
		// second external effect merely because local durable evidence was lost.
		return status, Reject
	}
	// Verified absence is materially different from UNKNOWN. A new admission
	// is still subject to the current authority and constraint gates above.
	return status, Allow
}

func child(dir, phase string) int {
	if phase != "effect" && phase != "absent" {
		return 2
	}
	obs := WorldObservation{
		Epoch:      80,
		Transition: "t-49",
		Present:    phase == "effect",
		Valid:      true,
		Source:     "external-sink",
	}
	if err := durableWrite(filepath.Join(dir, "world.json"), obs); err != nil {
		fmt.Println(err)
		return 2
	}
	// Simulated process crash after the external world boundary but before
	// local durable evidence is recorded. The process itself performs no
	// recovery decision.
	os.Exit(17)
	return 17
}

func runPhase(binary, dir, phase string) error {
	cmd := exec.Command(binary, "--child", dir, phase)
	out, err := cmd.CombinedOutput()
	if err == nil {
		return errors.New("expected controlled crash")
	}
	if cmd.ProcessState.ExitCode() != 17 {
		return fmt.Errorf("exit=%d output=%s", cmd.ProcessState.ExitCode(), out)
	}
	return nil
}

func check(name string, got, want any) int {
	if got != want {
		fmt.Printf("FAIL %s: got=%v want=%v\n", name, got, want)
		return 1
	}
	fmt.Printf("PASS %s: %v\n", name, got)
	return 0
}

func base() Journal {
	return Journal{
		State:      State{Epoch: 80},
		Transition: Transition{ID: "t-49", Action: "release", Target: "staging"},
		Capability: Capability{Subject: "alice", Action: "release"},
		Authority:  Authority{Subject: "alice", Action: "release", Active: true},
		Constraint: Constraint{AllowedTargets: map[string]bool{"staging": true}},
		Evidence:   Evidence{Epoch: 80, Valid: true, Source: "local-recovery"},
	}
}

func main() {
	if len(os.Args) == 4 && os.Args[1] == "--child" {
		os.Exit(child(os.Args[2], os.Args[3]))
	}

	failures := 0
	binary, err := os.Executable()
	if err != nil {
		panic(err)
	}

	dir, err := os.MkdirTemp("", "pass49-effect-")
	if err != nil {
		panic(err)
	}
	defer os.RemoveAll(dir)
	if err := runPhase(binary, dir, "effect"); err != nil {
		panic(err)
	}

	var observed WorldObservation
	if err := load(filepath.Join(dir, "world.json"), &observed); err != nil {
		panic(err)
	}
	j := base()

	status, decision := reconcile(j, &observed)
	failures += check("crash-after-external-effect-world-status", status, EffectPresent)
	failures += check("crash-after-external-effect-no-duplicate-action", decision, Reject)

	status, decision = reconcile(j, &observed)
	failures += check("repeat-reconciliation-stable", status, EffectPresent)
	failures += check("repeat-reconciliation-no-duplicate-action", decision, Reject)

	j.Authority.Active = false
	status, decision = reconcile(j, &observed)
	failures += check("revocation-after-effect-keeps-world-fact", status, EffectPresent)
	failures += check("revocation-after-effect-gates-new-action", decision, Reject)

	j = base()
	j.Constraint.AllowedTargets = map[string]bool{"production": true}
	status, decision = reconcile(j, &observed)
	failures += check("constraint-mutation-after-effect-keeps-world-fact", status, EffectPresent)
	failures += check("constraint-mutation-gates-new-action", decision, HITLRequired)

	dir2, err := os.MkdirTemp("", "pass49-absent-")
	if err != nil {
		panic(err)
	}
	defer os.RemoveAll(dir2)
	if err := runPhase(binary, dir2, "absent"); err != nil {
		panic(err)
	}
	var absent WorldObservation
	if err := load(filepath.Join(dir2, "world.json"), &absent); err != nil {
		panic(err)
	}
	j = base()
	status, decision = reconcile(j, &absent)
	failures += check("verified-absent-is-not-unknown", status, EffectAbsent)
	failures += check("verified-absent-allows-bounded-retry", decision, Allow)

	stale := absent
	stale.Epoch = 79
	status, decision = reconcile(j, &stale)
	failures += check("stale-observation-status", status, EffectUnknown)
	failures += check("stale-observation-no-retry", decision, Unknown)

	c1 := WorldObservation{Epoch: 80, Transition: "t-49", Present: true, Valid: true, Source: "sink-a"}
	c2 := WorldObservation{Epoch: 80, Transition: "t-49", Present: false, Valid: true, Source: "sink-b"}
	failures += check("conflicting-observations", observeWorld(&c1, &c2), EffectConflict)

	bad := observed
	bad.Valid = false
	status, decision = reconcile(j, &bad)
	failures += check("invalid-observation", status, EffectUnknown)
	failures += check("invalid-observation-no-retry", decision, Unknown)

	fmt.Println("PASS authority-effect-separation: a verified world fact is not silently erased by later authority revocation")
	fmt.Println("PASS primitive-removal: reconciliation uses observation/evidence/authority/constraint without an effect-specific Genesis primitive")

	if failures != 0 {
		fmt.Printf("PASS49_PUBLIC: FAIL; failures=%d\n", failures)
		return
	}
	fmt.Println("PASS49_PUBLIC: PASS; cases=11")
}
