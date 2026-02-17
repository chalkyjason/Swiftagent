# Distributing the MAUI Control Panel

The AgentUI project targets macOS Catalyst, iOS, Android, and Windows. This
guide covers building release artifacts for each platform.

---

## Prerequisites

| Tool | Install |
|------|---------|
| .NET SDK 8.0 | https://dotnet.microsoft.com/download |
| MAUI workload | `dotnet workload install maui` |
| Xcode 15+ (for macOS/iOS) | App Store |
| Android SDK (for Android) | Via Android Studio or `dotnet workload install android` |

---

## macOS (Catalyst) — .app bundle

```bash
cd AgentUI
dotnet publish -f net8.0-maccatalyst \
  -c Release \
  -p:CreatePackage=false \
  -o ./publish/macos
```

The `.app` bundle is written to `publish/macos/`. To create a distributable
`.pkg` for notarisation:

```bash
dotnet publish -f net8.0-maccatalyst \
  -c Release \
  -p:CreatePackage=true \
  -p:EnableCodeSigning=true \
  -p:CodesignKey="Developer ID Application: Your Name (TEAMID)" \
  -o ./publish/macos
```

Then notarise with `notarytool`:

```bash
xcrun notarytool submit publish/macos/*.pkg \
  --apple-id you@example.com \
  --password "@keychain:AC_PASSWORD" \
  --team-id TEAMID \
  --wait
```

---

## Windows — MSIX package

```bash
cd AgentUI
dotnet publish -f net8.0-windows10.0.19041.0 \
  -c Release \
  -p:WindowsPackageType=Msix \
  -o ./publish/windows
```

The MSIX installer is in `publish/windows/`. Sign it with your certificate:

```powershell
& "C:\Program Files (x86)\Windows Kits\10\bin\10.0.22621.0\x64\signtool.exe" `
  sign /fd SHA256 /a publish\windows\AgentUI*.msix
```

---

## iOS — .ipa

Building for iOS requires a macOS machine with Xcode installed.

```bash
cd AgentUI
dotnet publish -f net8.0-ios \
  -c Release \
  -p:ArchiveOnBuild=true \
  -p:RuntimeIdentifier=ios-arm64 \
  -p:CodesignKey="iPhone Distribution: Your Name (TEAMID)" \
  -p:CodesignProvision="Your Provisioning Profile" \
  -o ./publish/ios
```

The `.ipa` is written to `publish/ios/`. Upload to TestFlight:

```bash
xcrun altool --upload-app -f publish/ios/*.ipa \
  --type ios \
  --apiKey YOUR_API_KEY \
  --apiIssuer YOUR_ISSUER_ID
```

---

## Android — APK / AAB

```bash
cd AgentUI
# Debug APK (sideloading)
dotnet build -f net8.0-android -c Release -t:SignAndroidPackage

# Release AAB (Google Play)
dotnet publish -f net8.0-android \
  -c Release \
  -p:AndroidPackageFormat=aab \
  -o ./publish/android
```

Sign the AAB with your keystore before uploading to Google Play.

---

## Running the tests before publishing

```bash
cd AgentUI.Tests
dotnet test --logger "console;verbosity=normal"
```

All tests must pass before creating a release artifact.
