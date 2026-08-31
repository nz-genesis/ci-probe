package main

import (
	"sync"
	"testing"
)

func TestCapabilityDoesNotGrantAuthority(t *testing.T) {
	k, _ := newKernel(1)
	e := publicEnvelope("1")
	e.Authority = authority{Operations: []string{"other"}, Targets: []string{"probe-target"}}
	if got := k.execute(e, &probeRealizer{}); got != rejected { t.Fatalf("expected rejected, got %s", got) }
}

func TestACKIsNotVerified(t *testing.T) {
	k, _ := newKernel(1)
	if got := k.execute(publicEnvelope("1"), &probeRealizer{ack: true, observe: true}); got != observed { t.Fatalf("expected observed, got %s", got) }
}

func TestUnknownBlocksBlindRetry(t *testing.T) {
	k, _ := newKernel(1)
	r := &probeRealizer{ack: true, observe: false}
	e := publicEnvelope("1")
	if got := k.execute(e, r); got != unknown { t.Fatalf("expected unknown, got %s", got) }
	if got := k.execute(e, r); got != rejected { t.Fatalf("expected rejected blind retry, got %s", got) }
	r.mu.Lock(); calls := r.calls; r.mu.Unlock()
	if calls != 1 { t.Fatalf("realizer was called again: %d", calls) }
}

func TestUncertainRealizerErrorBlocksRetry(t *testing.T) {
	k, _ := newKernel(1)
	r := &probeRealizer{err: true}
	e := publicEnvelope("1")
	if got := k.execute(e, r); got != unknown { t.Fatalf("expected unknown, got %s", got) }
	if got := k.execute(e, r); got != rejected { t.Fatalf("expected rejected retry, got %s", got) }
}

func TestObservationBindingFailsClosed(t *testing.T) {
	k, _ := newKernel(1)
	if got := k.execute(publicEnvelope("1"), &probeRealizer{ack: true, observe: true, badID: true}); got != unknown { t.Fatalf("expected unknown, got %s", got) }
	k, _ = newKernel(1)
	if got := k.execute(publicEnvelope("1"), &probeRealizer{ack: true, observe: true, badDigest: true}); got != unknown { t.Fatalf("expected unknown, got %s", got) }
}

func TestConstraintCannotWiden(t *testing.T) {
	k, _ := newKernel(1)
	e := publicEnvelope("1")
	e.Constraints[0].Value = "different-target"
	if got := k.execute(e, &probeRealizer{}); got != rejected { t.Fatalf("expected rejected, got %s", got) }
}

func TestMalformedFailsClosed(t *testing.T) {
	k, _ := newKernel(1)
	e := publicEnvelope("")
	if got := k.execute(e, &probeRealizer{}); got != rejected { t.Fatalf("expected rejected, got %s", got) }
}

func TestHITLBoundary(t *testing.T) {
	k, _ := newKernel(1)
	e := publicEnvelope("1")
	e.Authority.RequiresHITL = true
	if got := k.execute(e, &probeRealizer{}); got != rejected { t.Fatalf("expected rejected, got %s", got) }
	e.Authority.ApprovedHITL = true
	if got := k.execute(e, &probeRealizer{ack: true, observe: true}); got != observed { t.Fatalf("expected observed, got %s", got) }
}

func TestBoundedConcurrentAdmission(t *testing.T) {
	k, _ := newKernel(1)
	var wg sync.WaitGroup
	accepted := 0
	var mu sync.Mutex
	for i := 0; i < 32; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if err := k.admit(publicEnvelope("same")); err == nil { mu.Lock(); accepted++; mu.Unlock() }
		}()
	}
	wg.Wait()
	if accepted != 1 { t.Fatalf("expected exactly one admission, got %d", accepted) }
}

func TestReconcileRejectsAlteredConstraints(t *testing.T) {
	k, _ := newKernel(1)
	e := publicEnvelope("1")
	r := &probeRealizer{ack: true, observe: false}
	if got := k.execute(e, r); got != unknown { t.Fatalf("expected unknown, got %s", got) }
	e.Constraints[0].Value = "different-target"
	if got := k.reconcile(e, r); got != rejected { t.Fatalf("expected rejected altered reconciliation, got %s", got) }
}

func TestPublicAdapterContainsOnlySyntheticFixture(t *testing.T) {
	e := publicEnvelope("public-disclosure-test")
	if e.Transition.Target != "probe-target" || e.Transition.Operation != "probe" || e.Transition.Payload != "public-fixture" { t.Fatal("unexpected fixture") }
}
