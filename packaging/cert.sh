#!/bin/sh
# Creates the local code signing certificate. A signed bundle keeps its TCC grants
# across rebuilds; an ad-hoc one pins the cdhash and loses them.
set -eu

NAME="WindowManager Local Signing"
KEYCHAIN="$HOME/Library/Keychains/login.keychain-db"

if security find-identity -v -p codesigning | grep -qF "$NAME"; then
    echo "certificate present: $NAME"
    exit 0
fi

DIR=$(mktemp -d)
trap 'rm -rf "$DIR"' EXIT
PASS=$(uuidgen)

openssl req -x509 -newkey rsa:2048 -nodes -days 3650 \
    -keyout "$DIR/key.pem" -out "$DIR/cert.pem" \
    -subj "/CN=$NAME" \
    -addext "basicConstraints=critical,CA:false" \
    -addext "keyUsage=critical,digitalSignature" \
    -addext "extendedKeyUsage=critical,codeSigning" 2>/dev/null

# security reads only the legacy PKCS#12 ciphers, not the OpenSSL 3 defaults
openssl pkcs12 -export -inkey "$DIR/key.pem" -in "$DIR/cert.pem" \
    -name "$NAME" -out "$DIR/bundle.p12" -passout pass:"$PASS" \
    -keypbe PBE-SHA1-3DES -certpbe PBE-SHA1-3DES -macalg sha1

security import "$DIR/bundle.p12" -k "$KEYCHAIN" -P "$PASS" -T /usr/bin/codesign >/dev/null

# codesign rejects a self-signed leaf until the certificate is a trusted root
echo "macOS asks for your login password to trust the certificate."
security add-trusted-cert -r trustRoot -p codeSign -k "$KEYCHAIN" "$DIR/cert.pem"

echo "created certificate: $NAME"
