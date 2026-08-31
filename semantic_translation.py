from dataclasses import dataclass
@dataclass(frozen=True)
class SourceRecord:
 sensor_id:str; temp_c:float; mode:str
@dataclass(frozen=True)
class TargetRecord:
 device:str; temperature_f:float; state:str
def translate(s): return TargetRecord(s.sensor_id,s.temp_c*9/5+32,s.mode)
def accepts(t): return t.temperature_f<=50 and t.state=='safe'
def source_pred(s): return s.temp_c<=10 and s.mode=='safe'
def main():
 s=SourceRecord('s1',10,'safe'); t=translate(s)
 checks=[source_pred(s)==accepts(t),accepts(t),translate(SourceRecord('s2',0,'safe')).temperature_f==32]
 wrong=TargetRecord('s3',10,'safe'); checks.append(not (source_pred(SourceRecord('s3',10,'safe')) and accepts(wrong) and wrong.temperature_f==50))
 bad=translate(SourceRecord('s4',11,'safe')); checks.append(not accepts(bad))
 bad2=TargetRecord('s5',51,'safe'); checks.append(not accepts(bad2))
 denied=translate(SourceRecord('s6',5,'unsafe')); checks.append(not accepts(denied))
 assert len(checks)==7 and all(checks); print('SEMANTIC TRANSLATION: 7/7 PASS')
main()
