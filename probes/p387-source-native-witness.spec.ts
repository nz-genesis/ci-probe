import 'fake-indexeddb/auto';
import { TestBed } from '@angular/core/testing';
import { RouterTestingModule } from '@angular/router/testing';
import { writeFileSync } from 'fs';
import { resolve } from 'path';
import { PouchdbService } from '../../database/pouchdb.service';
import { DevelopmentProcessRegistryModule } from '../development-process-registry.module';
import { DevelopmentMethod } from '../development-method/development-method';
import { BmPatternProcessDiagramModelerService } from '../bm-process/bm-pattern-process-diagram-modeler.service';
import { BmPatternProcessDiagramService } from '../bm-process/bm-pattern-process-diagram.service';
import * as BpmnUtils from '../bpmn/bpmn-utils';
import { ArtifactDataType } from './artifact-data';
import { MethodExecutionService } from './method-execution.service';
import { ProcessExecutionModelerService } from './process-execution-modeler.service';
import { ProcessExecutionService } from './process-execution.service';
import { RunningArtifact } from './running-artifact';
import { RunningPatternProcess } from './running-pattern-process';
import { RunningPatternProcessContextService } from './running-pattern-process-context.service';

const EXTERNAL_SHA = '4b49f93423cc2c17822f794a12187130c2c11202';
const RECEIPT_PATH = resolve(process.cwd(), 'p387-witness-receipt.json');
let dbSequence = 0;
let pouch: PouchdbService | undefined;
let databaseOpen = false;
const receipt: any = {
  schema: 'genesis.p387.source-native-witness.v1',
  status: 'IN_PROGRESS',
  externalRepository: 'SebastianGTTS/situational-business-model-developer',
  externalExpectedSha: EXTERNAL_SHA,
  externalObservedSha: process.env.P387_EXTERNAL_SHA ?? null,
  probeCommit: process.env.P387_PROBE_SHA ?? null,
  evidenceMode: 'REAL_CLASSES_REAL_BPMN_MODELER_REAL_POUCHDB_WITH_INDEXEDDB_POLYFILL',
  fixtureLimits: [
    'Selected input version is bound through the real MethodExecutionService.selectInputArtifacts API and its identity is recorded.',
    'Output version is a pre-seeded historical lineage fixture tied to the real execution ID; output generation is outside this witness.',
    'A real empty execution step completes the method lifecycle; no service/module is mocked.',
    'fake-indexeddb provides the IndexedDB API in Jest; this is not a physical-browser or disk-durability test.'
  ],
  trials: {}
};
function writeReceipt(): void {
  writeFileSync(RECEIPT_PATH, JSON.stringify(receipt, null, 2) + '\n');
}
function identity(value: unknown): string | null {
  if (value == null) return null;
  if (typeof value === 'string') return value;
  return JSON.stringify(value);
}
function errorText(error: unknown): string {
  return error instanceof Error ? (error.stack ?? error.message) : String(error);
}
async function runTrial(name: 'A' | 'B' | 'C', body: (record: any) => Promise<void>): Promise<void> {
  const record: any = { status: 'RUNNING' };
  receipt.trials[name] = record;
  writeReceipt();
  try {
    await body(record);
    record.status = 'PASS';
    writeReceipt();
  } catch (error) {
    record.status = 'FAIL';
    record.error = errorText(error);
    writeReceipt();
    throw error;
  }
}
async function createBranchedDiagram(): Promise<{ xml: string; startId: string }> {
  const service = TestBed.inject(BmPatternProcessDiagramModelerService);
  const modeler: any = await service.initModeling();
  try {
    const registry: any = modeler.get('elementRegistry');
    const modeling: any = modeler.get('modeling');
    const factory: any = modeler.get('elementFactory');
    const root: any = modeler.get('canvas').getRootElement();
    const elements: any[] = registry.getAll();
    const start: any = elements.find((e) => BpmnUtils.isStartEvent(e));
    if (!start) throw new Error('FIXTURE_SETUP: default BPMN start event not found');
    modeling.removeElements(elements.filter((e) => BpmnUtils.isSequenceFlow(e) || BpmnUtils.isEndEvent(e)));
    const shape = (type: string, id: string, x: number, y: number): any =>
      modeling.createShape(factory.createShape({ type, id }), { x, y }, root);
    const connect = (source: any, target: any, id: string): any => {
      const flow = modeling.connect(source, target, { type: 'bpmn:SequenceFlow', id });
      if (flow.id !== id) throw new Error('FIXTURE_SETUP: expected flow ' + id + ', got ' + flow.id);
      return flow;
    };
    const gateway = shape('bpmn:ExclusiveGateway', 'Gateway1', 320, 220);
    const taskA = shape('bpmn:Task', 'TaskA', 520, 120);
    const taskB = shape('bpmn:Task', 'TaskB', 520, 320);
    const endA = shape('bpmn:EndEvent', 'EndA', 740, 120);
    const endB = shape('bpmn:EndEvent', 'EndB', 740, 320);
    connect(start, gateway, 'FlowStartGateway');
    connect(gateway, taskA, 'FlowGatewayTaskA');
    connect(gateway, taskB, 'FlowGatewayTaskB');
    connect(taskA, endA, 'FlowTaskAEndA');
    connect(taskB, endB, 'FlowTaskBEndB');
    const xml = await service.getBmProcessDiagram(modeler);
    if (!xml || !xml.includes('FlowGatewayTaskA') || !xml.includes('FlowGatewayTaskB')) {
      throw new Error('FIXTURE_SETUP: serialized BPMN lost explicit branch flow IDs');
    }
    return { xml, startId: start.id };
  } finally {
    service.abortModeling(modeler);
  }
}
async function projection(processModel: RunningPatternProcess): Promise<any> {
  const service = TestBed.inject(ProcessExecutionModelerService);
  const modeler: any = await service.initModeling(processModel);
  try {
    const nodes = service.getNodes(modeler).map((n: any) => {
      const method = n.businessObject.get('method');
      return {
        id: n.id, type: n.businessObject.$type, tokens: service.getTokens(n),
        executed: Boolean(n.businessObject.get('executed')),
        method: method ? { name: method.name ?? null, id: method.id ?? null } : null
      };
    }).sort((a: any, b: any) => a.id.localeCompare(b.id));
    const flows = service.getFlows(modeler).map((f: any) => ({
      id: f.id, used: Boolean(f.businessObject.get('used'))
    })).sort((a: any, b: any) => a.id.localeCompare(b.id));
    return { xml: processModel.process.processDiagram, nodes, flows };
  } finally {
    service.abortModeling(modeler);
  }
}
async function snapshot(processModel: RunningPatternProcess): Promise<any> {
  const p = await projection(processModel);
  const versions = processModel.artifacts.flatMap((a: any) => a.versions.map((v: any) => ({
    artifactId: a._id, artifactName: a.name, versionId: v.id,
    createdBy: v.createdBy, executedBy: v.executedBy ?? null, dataIdentity: identity(v.data?.data)
  }))).sort((a: any, b: any) => (a.artifactName + ':' + a.versionId).localeCompare(b.artifactName + ':' + b.versionId));
  return {
    processId: processModel._id, processRevision: (processModel as any)._rev ?? null,
    diagramXml: processModel.process.processDiagram, projection: p,
    executionRecords: processModel.executedMethods.map((e: any) => ({
      executionId: e.executionId, nodeId: e.nodeId ?? null, methodName: e.methodName
    })).sort((a: any, b: any) => a.executionId.localeCompare(b.executionId)),
    runningMethods: processModel.runningMethods.map((m: any) => ({
      executionId: m.executionId, nodeId: m.nodeId ?? null, methodName: m.methodName
    })).sort((a: any, b: any) => a.executionId.localeCompare(b.executionId)),
    decisionNodeIds: Object.keys(processModel.process.decisions).sort(),
    artifactVersions: versions,
    removedMethods: (processModel.contextChangeInfo?.removedMethods ?? []).map((m: any) => ({
      id: m.id, executions: [...m.executions].sort(), methodName: m.decision?.method?.name ?? null
    })).sort((a: any, b: any) => a.id.localeCompare(b.id))
  };
}
async function createBaseline(label: string): Promise<any> {
  if (!pouch) throw new Error('FIXTURE_SETUP: PouchdbService was not injected');
  pouch.init('p387witness' + Date.now() + dbSequence++);
  databaseOpen = true;
  const context = TestBed.inject(RunningPatternProcessContextService);
  const executionService = TestBed.inject(ProcessExecutionService);
  const methodService = TestBed.inject(MethodExecutionService);
  const diagramService = TestBed.inject(BmPatternProcessDiagramService);
  const diagram = await createBranchedDiagram();
  const processModel = new RunningPatternProcess(undefined, {
    name: 'P387 source-native witness ' + label,
    contextChange: true,
    contextChangeInfo: {
      comment: 'Frozen P387 source-native behavioral witness',
      suggestedDomains: [], suggestedSituationalFactors: [],
      oldDomains: [], oldSituationalFactors: []
    },
    process: { initial: false, name: 'P387 exclusive-gateway fixture', processDiagram: diagram.xml, decisions: {} },
    artifacts: [{
      name: 'Input Artifact',
      artifact: { list: 'p387-witness', name: 'Input Artifact' },
      versions: [
        { id: 'input-v1', createdBy: 'manual', data: { type: ArtifactDataType.STRING, data: 'input-v1-data' } },
        { id: 'input-v2-selected', createdBy: 'manual', data: { type: ArtifactDataType.STRING, data: 'selected-input-v2-data' } }
      ]
    }]
  });
  const method = new DevelopmentMethod(undefined, {
    name: 'P387 Witness Method A',
    author: { name: 'P387 source-native witness' },
    executionSteps: [{
      name: 'No-op lifecycle step',
      description: 'Finish the real method lifecycle without mocking a module; output production is outside this witness.'
    }]
  });
  processModel.process.addDecision('TaskA', method);
  await diagramService.insertDevelopmentMethod(processModel.process, 'TaskA', method);
  await executionService.initRunningProcess(processModel);
  await executionService.moveToNextStep(processModel, diagram.startId);
  await executionService.moveToNextStep(processModel, 'Gateway1', 'FlowGatewayTaskA');
  const branch = await projection(processModel);
  const flowA = branch.flows.find((f: any) => f.id === 'FlowGatewayTaskA');
  const flowB = branch.flows.find((f: any) => f.id === 'FlowGatewayTaskB');
  const taskA = branch.nodes.find((n: any) => n.id === 'TaskA');
  const taskB = branch.nodes.find((n: any) => n.id === 'TaskB');
  if (!flowA?.used || flowB?.used || taskA?.tokens !== 1 || taskB?.tokens !== 0) {
    throw new Error('FIXTURE_SETUP: explicit exclusive-gateway branch selection was not observed');
  }
  const running = methodService.startMethodExecution(processModel, 'TaskA');
  methodService.selectInputArtifacts(processModel, running.executionId, [{ artifact: 0, version: 1 }]);
  const selected = running.inputArtifacts?.[0];
  if (!selected || selected.versionInfo.number !== 1 || identity(selected.data.data) !== 'selected-input-v2-data') {
    throw new Error('FIXTURE_SETUP: selected input version was not bound through the real selection service');
  }
  const selectedInput = {
    executionId: running.executionId, artifactIndex: 0, versionIndex: selected.versionInfo.number,
    createdBy: selected.versionInfo.createdBy, dataIdentity: identity(selected.data.data)
  };
  await methodService.prepareExecuteStep(processModel, running.executionId);
  await methodService.executeStep(processModel, running.executionId);
  await methodService.stopMethodExecution(processModel, running.executionId);
  await executionService.moveToNextMethod(processModel, 'TaskA');
  const execution = processModel.executedMethods.find((e: any) => e.executionId === running.executionId);
  if (!execution || execution.nodeId !== 'TaskA') {
    throw new Error('FIXTURE_SETUP: real method lifecycle did not create the expected execution record');
  }
  processModel.artifacts.push(new RunningArtifact(undefined, {
    name: 'Output Artifact',
    artifact: { list: 'p387-witness', name: 'Output Artifact' },
    versions: [{
      id: 'output-v1', createdBy: 'TaskA', executedBy: running.executionId,
      data: { type: ArtifactDataType.STRING, data: 'output-v1-data' }
    }]
  }));
  await pouch.post(processModel);
  const persisted = await context.get(processModel._id);
  const baseline = await snapshot(persisted);
  if (!baseline.projection.nodes.find((n: any) => n.id === 'TaskA')?.executed) {
    throw new Error('FIXTURE_SETUP: persisted baseline did not retain executed BPMN projection');
  }
  return {
    context, processId: persisted._id, executionId: running.executionId,
    branchSelection: {
      gatewayId: 'Gateway1', selectedFlowId: 'FlowGatewayTaskA', selectedFlowUsed: flowA.used,
      unselectedFlowId: 'FlowGatewayTaskB', unselectedFlowUsed: flowB.used,
      selectedTaskTokens: taskA.tokens, unselectedTaskTokens: taskB.tokens
    },
    selectedInput, outputVersionId: 'output-v1', baseline
  };
}
function artifactVersion(s: any, id: string): any {
  const v = s.artifactVersions.find((x: any) => x.versionId === id);
  if (!v) throw new Error('ASSERTION_FIXTURE: artifact version ' + id + ' missing');
  return v;
}
function node(s: any, id: string): any {
  const n = s.projection.nodes.find((x: any) => x.id === id);
  if (!n) throw new Error('ASSERTION_FIXTURE: BPMN node ' + id + ' missing');
  return n;
}
beforeAll(() => {
  receipt.status = 'IN_PROGRESS';
  receipt.externalObservedSha = process.env.P387_EXTERNAL_SHA ?? null;
  receipt.probeCommit = process.env.P387_PROBE_SHA ?? null;
  writeReceipt();
});
beforeEach(() => {
  TestBed.configureTestingModule({
    imports: [DevelopmentProcessRegistryModule, RouterTestingModule],
    providers: [PouchdbService]
  });
  pouch = TestBed.inject(PouchdbService);
});
afterEach(async () => {
  if (pouch && databaseOpen) { await pouch.closeDb(); databaseOpen = false; }
  pouch = undefined;
  TestBed.resetTestingModule();
});
afterAll(() => {
  const states = ['A', 'B', 'C'].map((k) => receipt.trials[k]?.status);
  receipt.status = states.every((s: string) => s === 'PASS') ? 'PASS' : 'FAIL_OR_INCOMPLETE';
  writeReceipt();
});

describe('P387 source-native behavioral witness (frozen external source)', () => {
  it('Trial A: resetExecutionToPosition changes BPMN projection without changing execution records or artifact lineage', async () => {
    await runTrial('A', async (r) => {
      const f = await createBaseline('A');
      r.branchSelection = f.branchSelection; r.selectedInputVersion = f.selectedInput; r.baseline = f.baseline; writeReceipt();
      const before = await snapshot(await f.context.get(f.processId)); r.before = before; writeReceipt();
      await f.context.resetExecutionToPosition(f.processId, 'TaskA');
      const after = await snapshot(await f.context.get(f.processId)); r.after = after; writeReceipt();
      expect(before.executionRecords).toEqual(after.executionRecords);
      expect(before.artifactVersions).toEqual(after.artifactVersions);
      expect(before.diagramXml).not.toBe(after.diagramXml);
      expect(node(before, 'TaskA').executed).toBe(true);
      expect(node(after, 'TaskA').executed).toBe(false);
      expect(node(before, 'TaskA').tokens).toBe(0);
      expect(node(after, 'TaskA').tokens).toBe(1);
      expect(after.projection.flows.every((flow: any) => flow.used === false)).toBe(true);
    });
  });
  it('Trial B: removeExecutedMethod deletes the execution record and resets attribution but retains version identity/data', async () => {
    await runTrial('B', async (r) => {
      const f = await createBaseline('B');
      r.branchSelection = f.branchSelection; r.selectedInputVersion = f.selectedInput; r.baseline = f.baseline; writeReceipt();
      const before = await snapshot(await f.context.get(f.processId)); r.before = before; writeReceipt();
      await f.context.removeExecutedMethod(f.processId, f.executionId);
      const after = await snapshot(await f.context.get(f.processId)); r.after = after; writeReceipt();
      expect(before.executionRecords).toHaveLength(1);
      expect(after.executionRecords).toHaveLength(0);
      const vb = artifactVersion(before, f.outputVersionId), va = artifactVersion(after, f.outputVersionId);
      expect(va.artifactId).toBe(vb.artifactId);
      expect(va.dataIdentity).toBe(vb.dataIdentity);
      expect(va.createdBy).toBe('added');
      expect(va.executedBy).toBeNull();
      expect(after.artifactVersions.filter((v: any) => v.artifactName === 'Input Artifact'))
        .toEqual(before.artifactVersions.filter((v: any) => v.artifactName === 'Input Artifact'));
      expect(node(before, 'TaskA').executed).toBe(true);
      expect(node(after, 'TaskA').executed).toBe(false);
      expect(before.diagramXml).not.toBe(after.diagramXml);
    });
  });
  it('Trial C: removeDevelopmentMethod preserves the execution record with detached node and manual attribution', async () => {
    await runTrial('C', async (r) => {
      const f = await createBaseline('C');
      r.branchSelection = f.branchSelection; r.selectedInputVersion = f.selectedInput; r.baseline = f.baseline; writeReceipt();
      const before = await snapshot(await f.context.get(f.processId)); r.before = before; writeReceipt();
      await f.context.removeDevelopmentMethod(f.processId, 'TaskA');
      const after = await snapshot(await f.context.get(f.processId)); r.after = after; writeReceipt();
      expect(before.executionRecords).toHaveLength(1);
      expect(after.executionRecords).toHaveLength(1);
      expect(after.executionRecords[0].executionId).toBe(f.executionId);
      expect(after.executionRecords[0].nodeId).toBeNull();
      const vb = artifactVersion(before, f.outputVersionId), va = artifactVersion(after, f.outputVersionId);
      expect(va.artifactId).toBe(vb.artifactId);
      expect(va.dataIdentity).toBe(vb.dataIdentity);
      expect(va.createdBy).toBe('manual');
      expect(va.executedBy).toBe(f.executionId);
      expect(after.artifactVersions.filter((v: any) => v.artifactName === 'Input Artifact'))
        .toEqual(before.artifactVersions.filter((v: any) => v.artifactName === 'Input Artifact'));
      expect(after.decisionNodeIds).not.toContain('TaskA');
      expect(node(before, 'TaskA').method).not.toBeNull();
      expect(node(after, 'TaskA').method).toBeNull();
      expect(node(after, 'TaskA').executed).toBe(false);
      expect(after.removedMethods.some((m: any) => m.executions.includes(f.executionId))).toBe(true);
      expect(before.diagramXml).not.toBe(after.diagramXml);
    });
  });
});
