# Security and responsible disclosure

This is a repository of mathematics papers, with one script and its logs. The main risks are accidental disclosure of credentials, private paths, or personal information.

## Do not report publicly

Do not open a public issue containing:

- API keys, tokens, passwords, cookies, or private URLs;
- personally identifying information not already part of the public papers;
- a reproducible path to extracting non-public material.

For a sensitive report, contact the maintainer at `lgboim@gmail.com` with the subject `unique-games-short-proof repository disclosure`. Include only the minimum information needed to reproduce the problem.

Mathematical errors, presentation problems and non-sensitive Lean check questions should use the public issue templates.

## Known false positive

A GitGuardian scan flagged `pw = pwd.getpwnam("ugcchk")` in `lean_check/ugc_lean_check.py` as a generic password; it is a Unix account lookup for the unprivileged user that the script creates with `useradd -M`, which has no password.
