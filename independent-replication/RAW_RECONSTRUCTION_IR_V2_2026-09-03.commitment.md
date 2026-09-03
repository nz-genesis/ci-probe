# IR-V2 raw reconstruction commitment

- protocol: `genesis-independent-replication-v1`
- challenge_id: `IR-V2`
- challenge_sha256: `03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`
- submission_sha256: `32ff0a750fa45d55f2963c4f653135e06342915ef8469e0d1eab22eb90fa59f8`
- submission_bytes: `21376`
- commitment_sha256: `8ddb9b82d17df3890739b91cf7de1d493c3569b1ce6461cc739d062a197c5650`
- hash_algorithm: `SHA256(raw_submission_bytes + UTF-8 newline byte + nonce_UTF8)`
- status: `COMMITMENT_BEFORE_REVEAL`

The raw report and nonce are intentionally not included in this commitment
record. The exact report bytes and nonce are revealed in the subsequent
publication commit.
