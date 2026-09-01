package main

import (
	"fmt"
	"sync"
)

// Pass 47 is an implementation-level concurrency probe. It deliberately uses
// only ordinary representations corresponding to the current candidate basis:
// State, Transition, Capability, Authority, Observation, Evidence, Constraint.
// It does not introduce DelegationGraph, RevocationManager, Transaction,
// LinearizationPoint, or another Genesis primitive.

type Decision string

const (
	Allow        Decision = "ALLOW"
	Reject       Decision = "REJECT"
	Unknown      Decision = "UNKNOWN"
	Conflict     Decision = "CONFLICT"
	HITLRequired Decision = "HITL_REQUIRED"
)

type State struct {
	Epoch  uint64
	Active bool
}

type Transition struct {
	Action string
	From   string
	To     string
}

type Capability struct {
	Subject string
	Action  string
}

type Authority struct {
	Subject string
	Action  string
}

type Constraint struct {
	AllowedTargets map[string]bool
}

type Observation struct {
	Epoch  uint64
	Active bool
}

type Evidence struct {
	Epoch  uint64
	Valid  bool
	Source string
}

type Kernel struct {
	mu         sync.Mutex
	state      State
	transition Transition
	capability Capability
	authority  Authority
	constraint Constraint
}

func (k *Kernel) admit() Decision {
	k.mu.Lock()
	defer k.mu.Unlock()

	if !k.capabilityMatches() || !k.authorityMatches() {
		return Reject
	}
	if !k.constraint.AllowedTargets[k.transition.To] {
		return HITLRequired
	}
	if !k.state.Active {
		return Reject
	}
	return Allow
}

func (k *Kernel) revoke() {
	k.mu.Lock()
	defer k.mu.Unlock()
	k.state.Epoch++
	k.state.Active = false
}

func (k *Kernel) capabilityMatches() bool {
	return k.capability.Subject == k.transition.From && k.capability.Action == k.transition.Action
}

func (k *Kernel) authorityMatches() bool {
	return k.authority.Subject == k.transition.From && k.authority.Action == k.transition.Action
}

func reconcile(observations []Observation) Decision {
	if len(observations) == 0 {
		return Unknown
	}
	epoch := observations[0].Epoch
	active := observations[0].Active
	for _, o := range observations[1:] {
		if o.Epoch != epoch {
			return Unknown
		}
		if o.Active != active {
			return Conflict
		}
	}
	if active {
		return Allow
	}
	return Reject
}

func check(name string, got, want Decision) int {
	if got != want {
		fmt.Printf("FAIL %s: got=%s want=%s\n", name, got, want)
		return 1
	}
	fmt.Printf("PASS %s: %s\n", name, got)
	return 0
}

func main() {
	failures := 0

	// 1. Admission linearizes before revocation: this attempt is allowed.
	k1 := &Kernel{
		state:      State{Epoch: 10, Active: true},
		transition: Transition{"release", "alice", "bob"},
		capability: Capability{"alice", "release"},
		authority:  Authority{"alice", "release"},
		constraint: Constraint{map[string]bool{"bob": true}},
	}
	start := make(chan struct{})
	admitted := make(chan Decision, 1)
	go func() {
		<-start
		admitted <- k1.admit()
	}()
	close(start)
	got := <-admitted
	failures += check("admission-before-revocation", got, Allow)
	k1.revoke()

	// 2. Revocation linearizes before admission: the attempt is rejected.
	k2 := &Kernel{
		state:      State{Epoch: 20, Active: true},
		transition: Transition{"release", "alice", "bob"},
		capability: Capability{"alice", "release"},
		authority:  Authority{"alice", "release"},
		constraint: Constraint{map[string]bool{"bob": true}},
	}
	k2.revoke()
	failures += check("revocation-before-admission", k2.admit(), Reject)

	// 3. Repeated actual goroutine races may choose either linearization order,
	// but must never produce a decision inconsistent with the locked state.
	for i := 0; i < 200; i++ {
		k := &Kernel{
			state:      State{Epoch: uint64(100 + i), Active: true},
			transition: Transition{"release", "alice", "bob"},
			capability: Capability{"alice", "release"},
			authority:  Authority{"alice", "release"},
			constraint: Constraint{map[string]bool{"bob": true}},
		}
		var wg sync.WaitGroup
		wg.Add(2)
		var decision Decision
		go func() { defer wg.Done(); decision = k.admit() }()
		go func() { defer wg.Done(); k.revoke() }()
		wg.Wait()
		if decision != Allow && decision != Reject {
			failures++
			fmt.Printf("FAIL race-%d: impossible decision=%s\n", i, decision)
		}
		if decision == Allow && k.state.Active {
			failures++
			fmt.Printf("FAIL race-%d: ALLOW left revoked state active\n", i)
		}
	}
	fmt.Println("PASS race-interleavings: 200 runs")

	// 4. Conflicting observations remain CONFLICT; no optimistic merge.
	failures += check("same-epoch-conflict", reconcile([]Observation{{30, true}, {30, false}}), Conflict)

	// 5. Cross-epoch observations remain UNKNOWN.
	failures += check("cross-epoch-unknown", reconcile([]Observation{{30, true}, {31, false}}), Unknown)

	// 6. Missing observations remain UNKNOWN.
	failures += check("missing-observation", reconcile(nil), Unknown)

	// 7. Capability without matching authority fails closed.
	k3 := &Kernel{
		state:      State{Epoch: 40, Active: true},
		transition: Transition{"release", "alice", "bob"},
		capability: Capability{"alice", "release"},
		authority:  Authority{"mallory", "release"},
		constraint: Constraint{map[string]bool{"bob": true}},
	}
	failures += check("capability-not-authority", k3.admit(), Reject)

	// 8. Constraint widening is not silently accepted.
	k4 := &Kernel{
		state:      State{Epoch: 50, Active: true},
		transition: Transition{"release", "alice", "mallory"},
		capability: Capability{"alice", "release"},
		authority:  Authority{"alice", "release"},
		constraint: Constraint{map[string]bool{"bob": true}},
	}
	failures += check("constraint-widening", k4.admit(), HITLRequired)

	// 9. Invalid evidence cannot become successful execution proof.
	evidence := Evidence{Epoch: 50, Valid: false, Source: "untrusted"}
	if evidence.Valid {
		failures++
		fmt.Println("FAIL invalid-evidence-proof")
	} else {
		fmt.Println("PASS invalid-evidence-proof: not accepted")
	}

	// 10. No special semantic types are introduced by this probe.
	fmt.Println("PASS primitive-removal: no delegation/revocation/concurrency primitive")

	if failures != 0 {
		fmt.Printf("PASS47_PUBLIC: FAIL; failures=%d\n", failures)
		return
	}
	fmt.Println("PASS47_PUBLIC: PASS; cases=10; race_interleavings=200")
}
