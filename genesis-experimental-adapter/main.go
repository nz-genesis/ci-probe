package main

import (
	"errors"
	"fmt"
	"sync"
)

type outcome string

const (
	rejected outcome = "REJECTED"
	observed outcome = "OBSERVED"
	unknown  outcome = "UNKNOWN"
)

type transition struct {
	ID        string
	Target    string
	Operation string
	Payload   string
}

type capability struct {
	Operations []string
	Targets    []string
}

type authority struct {
	Operations   []string
	Targets      []string
	RequiresHITL bool
	ApprovedHITL bool
}

type constraint struct {
	Key   string
	Value string
}

type envelope struct {
	Transition  transition
	Capability  capability
	Authority   authority
	Constraints []constraint
}

type observation struct {
	TransitionID string
}

type attempt struct {
	Ack         bool
	Observation *observation
}

type realizer interface {
	Execute(transition) attempt
	Reconcile(transition) attempt
}

type kernel struct {
	mu       sync.Mutex
	capacity int
	active   map[string]struct{}
	status   map[string]outcome
}

func newKernel(capacity int) (*kernel, error) {
	if capacity <= 0 {
		return nil, errors.New("capacity must be positive")
	}
	return &kernel{capacity: capacity, active: map[string]struct{}{}, status: map[string]outcome{}}, nil
}

func (k *kernel) admit(e envelope) error {
	if e.Transition.ID == "" || e.Transition.Target == "" || e.Transition.Operation == "" {
		return errors.New("malformed transition")
	}
	if !has(e.Capability.Operations, e.Transition.Operation) || !has(e.Capability.Targets, e.Transition.Target) {
		return errors.New("capability mismatch")
	}
	if !has(e.Authority.Operations, e.Transition.Operation) || !has(e.Authority.Targets, e.Transition.Target) {
		return errors.New("authority mismatch")
	}
	if e.Authority.RequiresHITL && !e.Authority.ApprovedHITL {
		return errors.New("HITL approval required")
	}
	for _, c := range e.Constraints {
		switch c.Key {
		case "target":
			if c.Value != e.Transition.Target {
				return errors.New("constraint target mismatch")
			}
		case "operation":
			if c.Value != e.Transition.Operation {
				return errors.New("constraint operation mismatch")
			}
		default:
			return errors.New("unknown constraint")
		}
	}
	k.mu.Lock()
	defer k.mu.Unlock()
	if _, ok := k.active[e.Transition.ID]; ok {
		return errors.New("duplicate active transition")
	}
	if _, ok := k.status[e.Transition.ID]; ok {
		return errors.New("duplicate terminal or uncertain transition")
	}
	if len(k.active) >= k.capacity {
		return errors.New("capacity exhausted")
	}
	k.active[e.Transition.ID] = struct{}{}
	return nil
}

func (k *kernel) execute(e envelope, r realizer) outcome {
	if err := k.admit(e); err != nil {
		return rejected
	}
	a := r.Execute(e.Transition)
	k.mu.Lock()
	delete(k.active, e.Transition.ID)
	k.mu.Unlock()
	if !a.Ack || a.Observation == nil {
		k.mu.Lock()
		k.status[e.Transition.ID] = unknown
		k.mu.Unlock()
		return unknown
	}
	k.mu.Lock()
	k.status[e.Transition.ID] = observed
	k.mu.Unlock()
	return observed
}

func (k *kernel) reconcile(e envelope, r realizer) outcome {
	k.mu.Lock()
	s := k.status[e.Transition.ID]
	k.mu.Unlock()
	if s != unknown {
		return rejected
	}
	a := r.Reconcile(e.Transition)
	if a.Observation == nil {
		return unknown
	}
	k.mu.Lock()
	k.status[e.Transition.ID] = observed
	k.mu.Unlock()
	return observed
}

func has(values []string, wanted string) bool {
	for _, v := range values {
		if v == wanted {
			return true
		}
	}
	return false
}

type probeRealizer struct {
	ack, observe bool
	calls         int
	mu            sync.Mutex
}

func (r *probeRealizer) Execute(t transition) attempt {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.calls++
	if !r.observe {
		return attempt{Ack: r.ack}
	}
	return attempt{Ack: r.ack, Observation: &observation{TransitionID: t.ID}}
}

func (r *probeRealizer) Reconcile(t transition) attempt {
	return attempt{Observation: &observation{TransitionID: t.ID}}
}

func publicEnvelope(id string) envelope {
	return envelope{
		Transition: transition{ID: id, Target: "probe-target", Operation: "probe", Payload: "public-fixture"},
		Capability: capability{Operations: []string{"probe"}, Targets: []string{"probe-target"}},
		Authority: authority{Operations: []string{"probe"}, Targets: []string{"probe-target"}},
		Constraints: []constraint{
			{Key: "target", Value: "probe-target"},
			{Key: "operation", Value: "probe"},
		},
	}
}

func main() {
	k, err := newKernel(2)
	if err != nil {
		panic(err)
	}
	if got := k.execute(publicEnvelope("public-1"), &probeRealizer{ack: true, observe: true}); got != observed {
		panic(fmt.Sprintf("expected observed, got %s", got))
	}
	fmt.Println("GENESIS_PUBLIC_CONTRACT_PROBE_OK")
}
