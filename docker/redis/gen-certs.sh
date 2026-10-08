#!/bin/sh

set -eu

TLS_DIR=/tls
DAYS="${REDIS_TLS_DAYS:-3650}"
SANS="${REDIS_TLS_SANS:-DNS:redis-queue,DNS:redis-cache,DNS:localhost,IP:127.0.0.1}"
ORG="${REDIS_TLS_ORG:-local}"
REDIS_UID="${REDIS_UID:-999}"
RENEW_WINDOW=2592000

log () {echo "[redis-tls] $*";}

mkdir -p "$TLS_DIR"
cd "$TLS_DIR"

issue_serve=1
if ["${REDIS_TLS_FORCE_REGEN:-0}" = "1"]; then
    log "REDIS_TLS_FORCE_REGEN=1 - discarding the CA and re-issuing"
    rm -f ca.crt ca.key ca.srl server.crt server.key server.sans client.crt client.key
elif [ -f server.crt ] && [ "$(cat server.sans 2>/dev/null)" != "$SANS" ]; then
    log "REDIS_TLS_SANS changed - re-issuing server.crt under the existing CA"
elif [ -f server.crt ] && openssl x509 -in server.crt -noout -checkend "$RENEW_WINDOW" >/dev/null 2>&1; then
    log "server.crt is successful for at least 30 days"
    issue_server=0
elif [ -f server.crt]; then
    log "server.crt expires within 30 days"
fi

if [ ! -f ca.crt ]; then
    log "issuing a private CA, valid ${DAYS}d"
    openssl req -x509 -newkey rsa:4096 -sha256 -nodes -days "$DAYS" \
        -keyout ca.key -out ca.crt \
        -subj "/O=$ORG/CN=$ORG Redis CA" \
        -addext "basicConstraints=critical,CA:TRUE,pathlen:0" \
        -addext "keyUsage=critical,keyCertSign,cRLSign"
else 
    log "reuse the existing CA"
fi

if [ "$issue_server" = "1" ]; then
    log "issuing the server certificate for $SANS"
    openssl req -new -newkey rsa:2048 -nodes -keyout server.key -out server.csr \
        -subj "/O=$ORG/CN=redis"
    cat > server.ext <<EOF
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=serverAuth
subjectAltName=$SANS
EOF
    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out server.crt -days "$DAYS" -sha256 -extfile server.ext 
    rm -f server.csr server.ext
    printf '%s\n' "$SANS" > server.sans
    log "server.crt was issued — if the servers are already running, restart them:"
    log "docker compose -f docker-compose.redis.yml restart redis-queue redis-cache"
fi

if [ "${REDIS_TLS_CLIENT_AUTH:-no}" = "yes" ] \
    && ! openssl x509 -in client.crt -noout -checkend "$RENEW_WINDOW" >/dev/null 2>&1; then
    log "issuing a client certificate (REDIS_TLS_CLIENT_AUTH=yes)"
    openssl req -new -newkey rsa:2048 -nodes -keyout client.key -out client.csr \
        -subj "/O=$ORG/CN=redis-client"
    cat > client.ext <<EOF
basicConstraints=critical,CA:FALSE
keyUsage=critical,digitalSignature,keyEncipherment
extendedKeyUsage=clientAuth
EOF
    openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial \
        -out client.crt -days "$DAYS" -sha256 -extfile client.ext
    rm -f client.csr client.ext
    chown 0:0 client.key && chmod 600 client.key
    chmod 644 client.crt
fi

chown "$REDIS_UID:$REDIS_UID" server.key server.crt 2>/dev/null || true
chown 0:0 ca.key 2>/dev/null || true
chmod 600 server.key ca.key
chmod 644 server.crt ca.crt

log "completed."
openssl x509 -in server.crt -noout -subject -issuer -enddate -ext subjectAltName | sed 's/^/[redis-tls]   /'
