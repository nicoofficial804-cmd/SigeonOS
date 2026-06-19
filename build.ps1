# Custom Arch ISO Builder
# This script runs the Arch Linux container in privileged mode to build the ISO.

$sigeonPath = $PSScriptRoot
Write-Host "Starting ..." -ForegroundColor Cyan
Write-Host "Workspace: $sigeonPath" -ForegroundColor Gray

# Ensure Docker is running
docker ps > $null 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Error "Docker is not running. Please start Docker Desktop and try again."
    exit 1
}

# Run the container
docker run --rm --privileged -v "${sigeonPath}:/mnt/sigeon" archlinux:latest bash -c "
    sed -i 's/\r$//' /mnt/sigeon/build_internal.sh
    chmod +x /mnt/sigeon/build_internal.sh
    /mnt/sigeon/build_internal.sh
"

if ($LASTEXITCODE -eq 0) {
    Write-Host "Success! The ISO is located at: $sigeonPath\sigeon-arch.iso" -ForegroundColor Green
} else {
    Write-Error "ISO build failed."
}
