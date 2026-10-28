param([switch]$UseWindowsCertificateTrust)

$ErrorActionPreference = 'Stop'
$root = Split-Path $PSScriptRoot -Parent
$secretDirectory = Join-Path $root '.jenkins-secrets'
$passwordPath = Join-Path $secretDirectory 'admin-password'

if (-not (Test-Path $passwordPath)) {
    New-Item -ItemType Directory -Force -Path $secretDirectory | Out-Null
    $password = [Guid]::NewGuid().ToString('N') + [Guid]::NewGuid().ToString('N')
    [IO.File]::WriteAllText($passwordPath, $password)
}

if ($UseWindowsCertificateTrust) {
    $tcp = [Net.Sockets.TcpClient]::new('updates.jenkins.io', 443)
    $tls = [Net.Security.SslStream]::new($tcp.GetStream(), $false)
    try {
        $tls.AuthenticateAsClient('updates.jenkins.io')
        $certificate = [Security.Cryptography.X509Certificates.X509Certificate2]::new($tls.RemoteCertificate)
        $chain = [Security.Cryptography.X509Certificates.X509Chain]::new()
        if (-not $chain.Build($certificate)) {
            throw 'Windows could not validate the Jenkins download certificate chain.'
        }
        for ($i = 1; $i -lt $chain.ChainElements.Count; $i++) {
            $bytes = $chain.ChainElements[$i].Certificate.Export(
                [Security.Cryptography.X509Certificates.X509ContentType]::Cert
            )
            $base64 = [Convert]::ToBase64String($bytes, [Base64FormattingOptions]::InsertLineBreaks)
            $pem = "-----BEGIN CERTIFICATE-----`n$base64`n-----END CERTIFICATE-----`n"
            [IO.File]::WriteAllText((Join-Path $PSScriptRoot "certs\issuer-$i.crt"), $pem)
        }
    } finally {
        $tls.Dispose()
        $tcp.Dispose()
    }
}

docker compose -f (Join-Path $root 'compose.jenkins.yml') up --build -d
if ($LASTEXITCODE -ne 0) {
    throw 'Jenkins failed to start. Check the Docker build output above.'
}

Write-Host 'Jenkins is starting at http://localhost:8081.'
Write-Host 'Username: admin'
Write-Host "The password is stored locally in $passwordPath. Do not commit or share it."
