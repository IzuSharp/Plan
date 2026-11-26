# Independent source review: PG-codec-B

Reviewed candidate `23845016b707a2876e6777cf935667dc546ca6d5` against baseline `7ff7b57b907b689defb880b8af62d83679608603`. Read the complete modified `contracts.cpp` helpers and relevant `Codec::validate`/`validate_scalar`, original `parse_json`/`number`/`parse_codec`, scalar `check_profile`/`postgres_compatible`/`postgres_decode_into`, and the added tests. This is source review, not independently executed correctness or performance credit.

## Result

No source-level contract blocker found. The fast path's accepted domain equals the old valid domain: exact bytes `{"precision":P,"scale":S}`, ordinary decimal digits without leading zeroes, P from 1 to 29, S from 0 through min(P,28). The original validator required numeric integral values in those ranges and exact equality to its `std::to_string` reconstruction. There are exactly 463 combinations. The new prefix, digit, separator, end-of-string, range and overflow checks accept all and only those combinations.

Every input not accepted by that fast path still executes the original JSON validator. Missing configuration and unsupported SQLite profile checks precede it unchanged. Whitespace, reordered/escaped/duplicate/extra keys, malformed JSON, fractions/exponents/signs/leading zeroes, integer overflow and appended NUL retain the old rejection path and diagnostics. The numeric parser consumes an explicitly bounded string_view; no input pointer outlives the call and no mutable Codec decision is cached.

`validate_scalar` still calls `codec.validate` first. Its later precision/scale parse therefore receives a canonical configuration for every valid stable Codec. Its defensive nullopt error is unreachable in the supported sequential path. Unsynchronized concurrent mutation of the same std::string was already a C++ data race and is not introduced as a supported use. Sequential configuration changes are re-read immediately, as covered by the new mutation test.

The fixed-width, flags, canonical zero/trailing-zero rules, 96-bit coefficient loop, scale and precision arithmetic remain unchanged. New uint32 precision/scale are bounded to the old uint64 valid values; promotion in the existing digits expression preserves the calculation. Profile, OID and canonical scalar validation sites remain in their original order. The wrong-OID plus invalid-config tests specifically distinguish invalid-config code3 from shape code4.

SQLite rejects codec13 before the fast parser. Ordinary SQLite decimal codec14 and FixedScaleMoney codec15 are unchanged. Shared contracts.cpp still requires both provider packages under the existing dependency planner; there is no public API or package-boundary change.

## Measurement and verification boundaries

The baseline source-scope evidence establishes four config JSON parses/three codec validations per nonnull configured decimal; it does not explain the Int64/string phase CPU gap. Candidate call/allocation counts, actual scalar/contracts/provider tests, independent packages/AOT and ordinary interleaved A/B are separate required evidence. No performance adoption follows from this source review.
