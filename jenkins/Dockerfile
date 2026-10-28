FROM docker:27-cli AS docker-cli

FROM jenkins/jenkins:lts-jdk21

USER root
COPY certs/ /usr/local/share/ca-certificates/assignment/
RUN update-ca-certificates \
    && for cert in /usr/local/share/ca-certificates/assignment/*.crt; do \
        if [ -f "$cert" ]; then \
            keytool -importcert -noprompt -cacerts -storepass changeit \
                -alias "assignment-$(basename "$cert")" -file "$cert"; \
        fi; \
    done
RUN apt-get update \
    && apt-get install -y --no-install-recommends python3 python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY --from=docker-cli /usr/local/bin/docker /usr/local/bin/docker
COPY --from=docker-cli /usr/local/libexec/docker/cli-plugins/docker-buildx /usr/local/libexec/docker/cli-plugins/docker-buildx

USER jenkins
RUN jenkins-plugin-cli --plugins workflow-aggregator git
COPY init.groovy /usr/share/jenkins/ref/init.groovy.d/assignment.groovy
