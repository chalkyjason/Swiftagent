# Distributing SwiftTamagotchi (iOS)

SwiftTamagotchi is a native SwiftUI iOS app. Distribution is done through the
standard Xcode / App Store toolchain.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Xcode | 15.0+ |
| Apple Developer account | Required for device installs and App Store |
| iOS Deployment Target | 16.0+ |

---

## Running tests

Before distributing, run the XCTest suite:

1. Open `SwiftTamagotchi/SwiftTamagotchi.xcodeproj` in Xcode.
2. Add the test target if not already present:
   - File → New → Target → Unit Testing Bundle
   - Name it `SwiftTamagotchiTests`
   - Add the two test files from `SwiftTamagotchi/SwiftTamagotchiTests/`:
     - `PetModelTests.swift`
     - `SaveManagerTests.swift`
3. Run tests: **Product → Test** (⌘U) or from the command line:

```bash
xcodebuild test \
  -project SwiftTamagotchi/SwiftTamagotchi.xcodeproj \
  -scheme SwiftTamagotchi \
  -destination 'platform=iOS Simulator,name=iPhone 15'
```

All tests must pass before archiving.

---

## Adding the test target to the Xcode project

The test files live in `SwiftTamagotchi/SwiftTamagotchiTests/`. To wire them up:

1. In Xcode, select the project in the Navigator.
2. Click **+** at the bottom of the Targets list.
3. Choose **Unit Testing Bundle**.
4. Set **Target to be Tested** to `SwiftTamagotchi`.
5. Add the two `.swift` test files to the new target's Compile Sources.

---

## Building a release .ipa (TestFlight / App Store)

### 1. Set the version and build number

In `SwiftTamagotchi.xcodeproj`, select the target → General:
- **Version**: e.g. `1.0.0`
- **Build**: increment with each submission (e.g. `1`, `2`, ...)

### 2. Archive

```bash
xcodebuild archive \
  -project SwiftTamagotchi/SwiftTamagotchi.xcodeproj \
  -scheme SwiftTamagotchi \
  -configuration Release \
  -archivePath ./build/SwiftTamagotchi.xcarchive
```

Or in Xcode: **Product → Archive**.

### 3. Export the .ipa

```bash
xcodebuild -exportArchive \
  -archivePath ./build/SwiftTamagotchi.xcarchive \
  -exportPath ./build/ipa \
  -exportOptionsPlist ExportOptions.plist
```

Create `ExportOptions.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store-connect</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
    <key>uploadSymbols</key>
    <true/>
    <key>compileBitcode</key>
    <false/>
</dict>
</plist>
```

### 4. Upload to App Store Connect / TestFlight

```bash
xcrun altool --upload-app \
  -f build/ipa/SwiftTamagotchi.ipa \
  --type ios \
  --apiKey YOUR_KEY_ID \
  --apiIssuer YOUR_ISSUER_UUID
```

Or drag the `.ipa` into **Transporter** (free on the Mac App Store).

---

## Sideloading for development (no Apple Developer account needed)

For testing on a personal device without a paid account:

1. In Xcode, sign in with your Apple ID (free account).
2. Set the Signing Team to your personal team.
3. Connect your iPhone via USB.
4. Select your device in the Xcode toolbar.
5. **Product → Run** (⌘R).

> Sideloaded apps expire after 7 days and must be re-installed. A paid developer
> account removes this limit.
