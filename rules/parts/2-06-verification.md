### VERIFICATION: verification

- **Rule VERIFICATION-1.** Verify by running the real thing. For a guard or
  hook, trigger the branch that should act and confirm its effect. A guard that
  stays quiet proves nothing.
- **Rule VERIFICATION-2.** Prove a fix with a test that fails without the fix.
- **Rule VERIFICATION-3.** Before you believe a failure, rule out a harness
  artifact or a false positive, and check whether the step produced its expected
  output.
- **Rule VERIFICATION-4.** In a non-deterministic domain, run the same
  configuration two or three times before you call a factor confirmed or ruled
  out. Tell the user what each experiment costs: compute, time, and anything the
  user must do by hand.
- **Rule VERIFICATION-5.** NEVER edit a file that a running job executes or
  reads. At minimum, write a temporary file and rename it over the original. Use
  a safer method when one fits better.
- **Rule VERIFICATION-6.** When you read a whole tree on storage where
  access-time updates are costly, open files without updating their access time.

