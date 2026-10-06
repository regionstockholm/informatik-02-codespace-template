FROM mcr.microsoft.com/devcontainers/base:2-bookworm

ARG SCT_VERSION=v0.27.0

RUN curl -fsSL "https://raw.githubusercontent.com/pacharanero/sct/${SCT_VERSION}/install.sh" -o /tmp/install-sct.sh && \
    SCT_VERSION="${SCT_VERSION}" SCT_INSTALL_DIR="/usr/local/bin" sh /tmp/install-sct.sh && \
    rm /tmp/install-sct.sh

# Create mount point directories with proper permissions
RUN mkdir -p /shared-not-stored-in-git /personal-not-stored-in-git && \
    chown -R vscode:vscode /shared-not-stored-in-git /personal-not-stored-in-git && \
    chmod -R 755 /shared-not-stored-in-git /personal-not-stored-in-git