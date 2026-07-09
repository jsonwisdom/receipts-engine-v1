# Transparency Trust Root

This directory publishes the public signing key used to verify the production seal tag.

```text
tag: production-seal-v0.1
key: 251400CB15AFAD89E1343BF11D194252DD42431C
fingerprint: 2514 00CB 15AF AD89 E134 3BF1 1D19 4252 DD42 431C
```

```bash
gpg --import transparency/signing_key.asc
git tag -v production-seal-v0.1
```

## Public Verification

Run:

    git fetch origin feat/alms-transparency-spec --tags
    gpg --import transparency/signing_key.asc
    cat transparency/fingerprint.txt
    git tag -v production-seal-v0.1
    git rev-parse production-seal-v0.1^{tag}
    git rev-parse production-seal-v0.1^{commit}
    sha256sum KEYS transparency/signing_key.asc transparency/fingerprint.txt transparency/README.md

Expected good signature from jsonwisdom <jaywisdom44@gmail.com>.

Expected tag object: 71d899fa818cc2c887a2175d2370c06115c8a5ab

Expected tag commit: 271a5a3c0f6eb76b4cb36288aaa25bfae29b1c44

CI status is not claimed by this receipt unless a separate workflow run artifact is added.

