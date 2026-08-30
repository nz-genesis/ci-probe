from dataclasses import dataclass

@dataclass(frozen=True)
class Receipt:
    commitment: str
    nonce: str
    realizer: str
    effect: str

class RaceVerifier:
    def __init__(self):
        self.consumed = set()

    def verify_and_consume(self, receipt: Receipt):
        key = (receipt.commitment, receipt.nonce)
        if key in self.consumed:
            return False
        self.consumed.add(key)
        return True

def main():
    receipt = Receipt("C1", "N1", "R1", "E1")
    a = RaceVerifier(); b = RaceVerifier()
    assert a.verify_and_consume(receipt) is True
    assert a.verify_and_consume(receipt) is False
    # Independent verifiers do not share consumption state: this is the
    # deliberate negative case demonstrating that local replay protection
    # is insufficient for distributed consumption.
    assert b.verify_and_consume(receipt) is True
    print("DISTRIBUTED REPLAY RACE: LOCAL-ONLY PROTECTION LIMIT CONFIRMED")
    print("local_replay_rejected=True")
    print("independent_verifier_replay_accepted=True")

if __name__ == "__main__":
    main()
