# Ceph idioms and how they map to CERT rules

Evidence is from a Ceph `main` checkout (file paths below). Counts are rough
greps in `src/` excluding vendored trees and `test/`; they only show how common
an idiom is. The machine-readable form is `profiles/ceph.yaml`.

## ceph_assert / ceph_abort (`src/include/ceph_assert.h`)
- `ceph_assert(expr)` and `ceph_assert_always(expr)` evaluate `expr` once; both are
  active in release builds today (the header says `ceph_assert` may become NDEBUG-sensitive).
  About 10k uses.
- Good for invariants (programmer error). Bad for validating anything that came from
  the network, disk, a client or a config value: that is a remote crash.
- Rules: ERR50-CPP (downgraded to note for these macros), EXP34-C, EXP30-C. PRE31-C is suppressed.
- Side effects inside an assert are discouraged by the header's own NDEBUG caveat.

## dout / ldout / derr / dendl (`src/common/dout.h`)
- Stream based (`*_dout << ...`), or a seastar logger in crimson. Not printf style.
- FIO30-C / FIO47-C apply only to real printf-family calls (`snprintf`, `sprintf`).
- Streaming an uninitialised or dangling object inside a log line is still EXP53/EXP54.

## buffer::list / bufferptr (`src/include/buffer.h`, `src/include/encoding.h`)
- Iterator `copy()` throws `buffer::end_of_buffer`; `ptr::operator[]` asserts.
  `DECODE_START`/`DECODE_FINISH` validate the versioned wrapper.
- Risks: raw `c_str()` + offset arithmetic, decoded lengths used for `resize()`/`reserve()`/loops
  before validation, decode that catches `buffer::error` and continues, `encode`/`decode` asymmetry.
- Rules: ARR30-C, ARR38-C, ARR39-C, INT30-C, INT31-C, CTR50-CPP, STR50-CPP, EXP53-CPP.

## ceph::mutex (`src/common/ceph_mutex.h`)
- `ceph::make_mutex("name")` gives a lockdep-instrumented mutex in debug builds and `std::mutex`
  in release. About 740 `ceph::mutex` uses against about 390 `std::mutex` uses in `src/`.
- Hold through `std::lock_guard`/`std::unique_lock`; `ceph_mutex_is_locked_by_me` documents
  "caller holds the lock" contracts. Condition variables: `ceph::condition_variable` with a predicate.
- Under `WITH_CRIMSON` the mutex is a dummy.
- Rules: CON50..CON56-CPP, CON31-C, CON41-C.

## RefCountedObject / ceph::ref_t (`src/common/RefCountedObj.h`)
- `nref` starts at 1; `ceph::make_ref<T>()` / `make_message<T>()` adopt correctly. `FRIEND_MAKE_REF`
  grants private-ctor access. `RefCountedObjectSafe` deletes `get()`/`put()`.
- Bugs to look for: `put()` then member access (MEM50/EXP54), `delete` on a refcounted object
  (MEM51), wrapping a raw pointer in an intrusive_ptr that adds a reference (leak), missing
  `put()` on an early return (MEM51), a raw pointer kept in a container without `get()`.

## Errors
- Functions return negative errno ints (`return -ENOENT`); `int r = ...;` then check. About 130
  `atoi/atol/atof` uses remain; `strict_strtol`, `strict_strtoll`, `strict_si_cast`
  (`src/common/strtol.h`) report failure. About 340 uses of the strict helpers.
- Rules: ERR33-C (raised), ERR34-C (raised), ERR30-C.

## Randomness
- `ceph::util::generate_random_number` (`src/include/random.h`) is the project default; secrets must
  come from `get_random_bytes`/OpenSSL. About 190 `rand()/random()/srand()` hits exist, mostly in
  `client/` and tools: MSC30-C / MSC50-CPP are worth reporting on new code only.

## Callbacks: asio, seastar, Context/Finisher
- Lambdas passed to `boost::asio`, `.then()`, `Context`/`Finisher` outlive the calling frame.
- Rules: EXP61-CPP (error), EXP54-CPP, MEM50-CPP, OOP53-CPP. Coroutine frames own their locals.

## crimson (`src/crimson`)
- ~160 source files, seastar futures, shard-per-core. `ceph::mutex` is a dummy; do not report CON rules,
  report future/lifetime problems.

## Third-party and test code
- Excluded by `exclude_paths` (`src/boost`, `src/rocksdb`, `src/seastar`, `src/spdk`, `src/fmt`, ...).
- `src/test` keeps only memory/expression/array rules.
