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
