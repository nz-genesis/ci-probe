package main

import (
	"crypto/sha256"
	"encoding/hex"
	"errors"
	"fmt"
	"sort"
	"strings"
	"sync"
)

type outcome string

const (
	rejected outcome = "REJECTED"
	observed outcome = "OBSERVED"
	unknown  outcome = "UNKNOWN"
)

type transition struct{ ID, Target, Operation, Payload string }
type capability struct{ ID string; Operations, Targets []string }
type authority struct { Principal string; Operations, Targets []string; RequiresHITL, ApprovedHITL bool }
type constraint struct{ Key, Value string }
type envelope struct{ Transition transition; Capability capability; Authority authority; Constraints []constraint }
type observation struct{ TransitionID, Digest string }
type attempt struct{ Ack bool; Observation *observation; Err error }
type realizer interface{ Execute(transition) attempt; Reconcile(transition) attempt }
type kernel struct { mu sync.Mutex; capacity int; active map[string]struct{}; status map[string]outcome; admissions map[string]string }

func newKernel(capacity int) (*kernel, error) {
	if capacity <= 0 { return nil, errors.New("capacity must be positive") }
	return &kernel{capacity: capacity, active: map[string]struct{}{}, status: map[string]outcome{}, admissions: map[string]string{}}, nil
}

func (k *kernel) admit(e envelope) error {
	if strings.TrimSpace(e.Transition.ID) == "" || strings.TrimSpace(e.Transition.Target) == "" || strings.TrimSpace(e.Transition.Operation) == "" { return errors.New("malformed transition") }
	if !has(e.Capability.Operations, e.Transition.Operation) || !has(e.Capability.Targets, e.Transition.Target) { return errors.New("capability mismatch") }
	if !has(e.Authority.Operations, e.Transition.Operation) || !has(e.Authority.Targets, e.Transition.Target) { return errors.New("authority mismatch") }
	if e.Authority.RequiresHITL && !e.Authority.ApprovedHITL { return errors.New("HITL approval required") }
	if err := validateConstraints(e.Transition, e.Constraints); err != nil { return err }
	fp := envelopeFingerprint(e)
	k.mu.Lock(); defer k.mu.Unlock()
	if _, ok := k.active[e.Transition.ID]; ok { return errors.New("duplicate active transition") }
	if _, ok := k.status[e.Transition.ID]; ok { return errors.New("duplicate terminal or uncertain transition") }
	if len(k.active) >= k.capacity { return errors.New("capacity exhausted") }
	k.active[e.Transition.ID] = struct{}{}; k.status[e.Transition.ID] = "ATTEMPTED"; k.admissions[e.Transition.ID] = fp
	return nil
}

func (k *kernel) execute(e envelope, r realizer) outcome {
	if err := k.admit(e); err != nil { return rejected }
	a := r.Execute(e.Transition)
	k.mu.Lock(); delete(k.active, e.Transition.ID); k.mu.Unlock()
	if a.Err != nil || !a.Ack || a.Observation == nil { k.mu.Lock(); k.status[e.Transition.ID] = unknown; k.mu.Unlock(); return unknown }
	if a.Observation.TransitionID != e.Transition.ID || strings.TrimSpace(a.Observation.Digest) == "" { k.mu.Lock(); k.status[e.Transition.ID] = unknown; k.mu.Unlock(); return unknown }
	k.mu.Lock(); k.status[e.Transition.ID] = observed; k.mu.Unlock(); return observed
}

func (k *kernel) reconcile(e envelope, r realizer) outcome {
	k.mu.Lock(); s := k.status[e.Transition.ID]; expected := k.admissions[e.Transition.ID]; k.mu.Unlock()
	if s != unknown || strings.TrimSpace(e.Transition.ID) == "" { return rejected }
	if err := validateConstraints(e.Transition, e.Constraints); err != nil { return rejected }
	if expected == "" || envelopeFingerprint(e) != expected { return rejected }
	a := r.Reconcile(e.Transition)
	if a.Observation == nil || a.Observation.TransitionID != e.Transition.ID || strings.TrimSpace(a.Observation.Digest) == "" { return unknown }
	k.mu.Lock(); k.status[e.Transition.ID] = observed; k.mu.Unlock(); return observed
}

func validateConstraints(t transition, cs []constraint) error {
	for _, c := range cs { switch c.Key { case "target": if c.Value != t.Target { return errors.New("constraint target mismatch") }; case "operation": if c.Value != t.Operation { return errors.New("constraint operation mismatch") }; case "payload-digest": if c.Value != digest(t.Payload) { return errors.New("constraint payload mismatch") }; default: return errors.New("unknown constraint") } }
	return nil
}

func envelopeFingerprint(e envelope) string {
	ops := append([]string(nil), e.Capability.Operations...); targets := append([]string(nil), e.Capability.Targets...); authOps := append([]string(nil), e.Authority.Operations...); authTargets := append([]string(nil), e.Authority.Targets...); cs := append([]constraint(nil), e.Constraints...)
	sort.Strings(ops); sort.Strings(targets); sort.Strings(authOps); sort.Strings(authTargets); sort.Slice(cs, func(i,j int) bool { if cs[i].Key == cs[j].Key { return cs[i].Value < cs[j].Value }; return cs[i].Key < cs[j].Key })
	return digest(fmt.Sprintf("id=%q|target=%q|operation=%q|payload=%q|cap-id=%q|cap-ops=%q|cap-targets=%q|principal=%q|auth-ops=%q|auth-targets=%q|hitl-required=%t|hitl-approved=%t|constraints=%q", e.Transition.ID, e.Transition.Target, e.Transition.Operation, e.Transition.Payload, e.Capability.ID, ops, targets, e.Authority.Principal, authOps, authTargets, e.Authority.RequiresHITL, e.Authority.ApprovedHITL, cs))
}
func has(values []string, wanted string) bool { for _, v := range values { if v == wanted { return true } }; return false }
func digest(s string) string { h := sha256.Sum256([]byte(s)); return hex.EncodeToString(h[:]) }

type probeRealizer struct { ack, observe, err, badID, missingDigest bool; calls int; mu sync.Mutex }
func (r *probeRealizer) Execute(t transition) attempt { r.mu.Lock(); defer r.mu.Unlock(); r.calls++; if r.err { return attempt{Ack:true, Err:errors.New("uncertain realizer error")} }; if !r.observe { return attempt{Ack:r.ack} }; id,d:=t.ID,digest(t.Payload); if r.badID { id="other" }; if r.missingDigest { d="" }; return attempt{Ack:r.ack, Observation:&observation{TransitionID:id,Digest:d}} }
func (r *probeRealizer) Reconcile(t transition) attempt { return attempt{Observation:&observation{TransitionID:t.ID,Digest:digest(t.Payload)}} }
func publicEnvelope(id string) envelope { return envelope{Transition:transition{ID:id,Target:"probe-target",Operation:"probe",Payload:"public-fixture"},Capability:capability{ID:"public-capability",Operations:[]string{"probe"},Targets:[]string{"probe-target"}},Authority:authority{Principal:"public-principal",Operations:[]string{"probe"},Targets:[]string{"probe-target"}},Constraints:[]constraint{{Key:"target",Value:"probe-target"},{Key:"operation",Value:"probe"},{Key:"payload-digest",Value:digest("public-fixture")}}} }
func main() { k,err:=newKernel(2); if err!=nil { panic(err) }; if got:=k.execute(publicEnvelope("public-1"),&probeRealizer{ack:true,observe:true}); got!=observed { panic(fmt.Sprintf("expected observed, got %s",got)) }; fmt.Println("GENESIS_PUBLIC_CONTRACT_PROBE_OK") }
