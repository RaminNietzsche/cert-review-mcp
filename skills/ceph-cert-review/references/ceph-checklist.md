# Ceph CERT review checklist

Run through this for each hunk before drafting a comment.

**Input and bounds**
- [ ] Does the value come from a message, an on-disk structure, a client request or a config option?
- [ ] Is a decoded length/count validated before `resize()`, `reserve()`, an allocation or a loop bound?
- [ ] Is `bl.c_str() + off` bounded by `bl.length()`? Prefer iterator `copy()` / `bufferptr` accessors.
- [ ] 64-bit offsets/sizes narrowed to `unsigned`/`int` (INT31-C)? Arithmetic on sizes wraps (INT30-C)?
- [ ] `ceph_assert` used on external data instead of returning `-EINVAL` / throwing a decode error?

**Lifetime**
- [ ] After `put()`/`release()`/`std::move`, is the object touched again?
- [ ] New objects deriving `RefCountedObject` created with `make_ref`/`make_message`, not `new` into a raw owner?
- [ ] A lambda handed to `Context`, `Finisher`, asio or seastar: does it capture locals, `this` or references? Is `this` alive when it runs?
- [ ] `string_view`/`span`/`c_str()` stored longer than the owning string/bufferlist?
- [ ] Iterators/references into a container kept across `insert`/`erase`/`resize` (CTR51-CPP)?

**Concurrency** (skip in `src/crimson`)
- [ ] Locks taken with `std::lock_guard`/`unique_lock`, never bare `lock()`/`unlock()` pairs?
- [ ] `ceph::mutex` from `ceph::make_mutex`, not `std::mutex`?
- [ ] Condition wait with a predicate? Lock held across a call into another component?
- [ ] Atomic read-modify-write sequences written as separate load/store?

**Errors**
- [ ] `int r = ...` and no check; return value of a syscall wrapper ignored?
- [ ] `atoi`/`strtol` instead of `strict_strtol`/`from_chars`?
- [ ] `throw`ing in a destructor, `catch (...)` swallowing, static initialisers that can throw?

**Process**
- [ ] Is the file test, benchmark or generated code? Then only memory/array/expression rules count.
- [ ] Is the finding on a changed line? Do not review untouched legacy code in a PR comment.
- [ ] Does the suggested fix match CodingStyle (2-space indent, braces on every `if`)?
