# Mobile Application Security Template

Use this template for implementing security best practices in iOS and Android applications.

## Mobile Security Checklist (OWASP MASVS)

### Data Storage
- [ ] Sensitive data encrypted at rest
- [ ] No sensitive data in logs
- [ ] Secure key storage (Keychain/Keystore)
- [ ] Auto-lock after inactivity
- [ ] Clear clipboard after timeout

### Authentication
- [ ] Multi-factor authentication support
- [ ] Biometric authentication (Face ID/Touch ID)
- [ ] Certificate pinning for API calls
- [ ] Secure session management
- [ ] OAuth 2.0 with PKCE

### Network Security
- [ ] TLS 1.3 for all connections
- [ ] Certificate pinning implemented
- [ ] No sensitive data in URLs
- [ ] API request/response validation
- [ ] WebView security hardening

### Code Security
- [ ] Code obfuscation enabled
- [ ] No hardcoded secrets
- [ ] Jailbreak/root detection
- [ ] Anti-debugging measures
- [ ] Secure random number generation

### Platform Security
- [ ] Latest SDK version
- [ ] Secure intent handling (Android)
- [ ] Secure deep link validation
- [ ] App Transport Security (iOS)
- [ ] Android backup disabled for sensitive data

## iOS Security Implementation

### Secure Data Storage (Swift)

```swift
// SecureStorage.swift - Using iOS Keychain
import Foundation
import Security

class SecureStorage {

    // MARK: - Save to Keychain

    static func save(key: String, value: String) -> Bool {
        guard let data = value.data(using: .utf8) else {
            return false
        }

        // Delete existing item first
        delete(key: key)

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessible as String: kSecAttrAccessibleWhenUnlockedThisDeviceOnly // Device-specific
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }

    // MARK: - Retrieve from Keychain

    static func load(key: String) -> String? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]

        var result: AnyObject?
        let status = SecItemCopyMatching(query as CFDictionary, &result)

        guard status == errSecSuccess,
              let data = result as? Data,
              let value = String(data: data, encoding: .utf8) else {
            return nil
        }

        return value
    }

    // MARK: - Delete from Keychain

    static func delete(key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]

        SecItemDelete(query as CFDictionary)
    }

    // MARK: - Save Sensitive Data with Biometric Protection

    static func saveBiometric(key: String, value: String) -> Bool {
        guard let data = value.data(using: .utf8) else {
            return false
        }

        delete(key: key)

        // Create access control for biometric authentication
        guard let access = SecAccessControlCreateWithFlags(
            nil,
            kSecAttrAccessibleWhenUnlockedThisDeviceOnly,
            .biometryCurrentSet, // Requires Face ID/Touch ID
            nil
        ) else {
            return false
        }

        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data,
            kSecAttrAccessControl as String: access
        ]

        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }
}

// Usage
SecureStorage.save(key: "authToken", value: "sensitive_token_here")
let token = SecureStorage.load(key: "authToken")
```

### Certificate Pinning (Swift + Alamofire)

```swift
// NetworkManager.swift
import Foundation
import Alamofire

class NetworkManager {

    static let shared = NetworkManager()
    private let session: Session

    private init() {
        // Certificate pinning configuration
        let evaluators: [String: ServerTrustEvaluating] = [
            "api.yourdomain.com": PinnedCertificatesTrustEvaluator(
                certificates: [
                    // Load certificate from bundle
                    NetworkManager.certificate(filename: "api_certificate")!
                ],
                acceptSelfSignedCertificates: false,
                performDefaultValidation: true,
                validateHost: true
            )
        ]

        let serverTrustManager = ServerTrustManager(evaluators: evaluators)

        self.session = Session(
            serverTrustManager: serverTrustManager
        )
    }

    // MARK: - Helper: Load Certificate

    private static func certificate(filename: String) -> SecCertificate? {
        guard let path = Bundle.main.path(forResource: filename, ofType: "cer"),
              let data = try? Data(contentsOf: URL(fileURLWithPath: path)) else {
            return nil
        }

        return SecCertificateCreateWithData(nil, data as CFData)
    }

    // MARK: - API Request

    func request<T: Decodable>(
        _ endpoint: String,
        method: HTTPMethod = .get,
        parameters: Parameters? = nil,
        completion: @escaping (Result<T, Error>) -> Void
    ) {
        session.request(
            "https://api.yourdomain.com\(endpoint)",
            method: method,
            parameters: parameters,
            encoding: JSONEncoding.default
        )
        .validate()
        .responseDecodable(of: T.self) { response in
            switch response.result {
            case .success(let value):
                completion(.success(value))
            case .failure(let error):
                completion(.failure(error))
            }
        }
    }
}
```

### Biometric Authentication (Swift)

```swift
// BiometricAuth.swift
import LocalAuthentication

class BiometricAuth {

    enum BiometricType {
        case faceID
        case touchID
        case none
    }

    enum AuthError: Error {
        case biometricNotAvailable
        case biometricNotEnrolled
        case authenticationFailed
        case userCancel
        case userFallback
    }

    // MARK: - Check Biometric Availability

    static func biometricType() -> BiometricType {
        let context = LAContext()
        var error: NSError?

        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            return .none
        }

        switch context.biometryType {
        case .faceID:
            return .faceID
        case .touchID:
            return .touchID
        default:
            return .none
        }
    }

    // MARK: - Authenticate

    static func authenticate(
        reason: String = "Authenticate to access your account",
        completion: @escaping (Result<Void, AuthError>) -> Void
    ) {
        let context = LAContext()
        var error: NSError?

        // Check if biometric authentication is available
        guard context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) else {
            if let error = error {
                switch error.code {
                case LAError.biometryNotEnrolled.rawValue:
                    completion(.failure(.biometricNotEnrolled))
                default:
                    completion(.failure(.biometricNotAvailable))
                }
            }
            return
        }

        // Perform authentication
        context.evaluatePolicy(
            .deviceOwnerAuthenticationWithBiometrics,
            localizedReason: reason
        ) { success, error in
            DispatchQueue.main.async {
                if success {
                    completion(.success(()))
                } else if let error = error as? LAError {
                    switch error.code {
                    case .userCancel:
                        completion(.failure(.userCancel))
                    case .userFallback:
                        completion(.failure(.userFallback))
                    default:
                        completion(.failure(.authenticationFailed))
                    }
                }
            }
        }
    }
}

// Usage
BiometricAuth.authenticate { result in
    switch result {
    case .success:
        print("Authentication successful")
        // Proceed with sensitive operation
    case .failure(let error):
        print("Authentication failed: \(error)")
    }
}
```

### Jailbreak Detection (Swift)

```swift
// JailbreakDetection.swift
import UIKit

class JailbreakDetection {

    // MARK: - Check if Device is Jailbroken

    static func isJailbroken() -> Bool {
        #if targetEnvironment(simulator)
        return false // Always allow simulator
        #else
        return checkSuspiciousFiles() || checkSuspiciousApps() || checkWriteAccess()
        #endif
    }

    // MARK: - Check for Suspicious Files

    private static func checkSuspiciousFiles() -> Bool {
        let suspiciousFiles = [
            "/Applications/Cydia.app",
            "/Library/MobileSubstrate/MobileSubstrate.dylib",
            "/bin/bash",
            "/usr/sbin/sshd",
            "/etc/apt",
            "/private/var/lib/apt/",
            "/private/var/lib/cydia",
            "/private/var/mobile/Library/SBSettings/Themes",
            "/private/var/tmp/cydia.log",
            "/System/Library/LaunchDaemons/com.ikey.bbot.plist",
            "/System/Library/LaunchDaemons/com.saurik.Cydia.Startup.plist"
        ]

        for path in suspiciousFiles {
            if FileManager.default.fileExists(atPath: path) {
                return true
            }
        }

        return false
    }

    // MARK: - Check for Suspicious Apps

    private static func checkSuspiciousApps() -> Bool {
        let suspiciousApps = [
            "cydia://",
            "sileo://",
            "zbra://",
            "undecimus://",
            "checkra1n://"
        ]

        for urlScheme in suspiciousApps {
            if let url = URL(string: urlScheme),
               UIApplication.shared.canOpenURL(url) {
                return true
            }
        }

        return false
    }

    // MARK: - Check Write Access to Restricted Areas

    private static func checkWriteAccess() -> Bool {
        let testPath = "/private/jailbreak_test.txt"

        do {
            try "test".write(toFile: testPath, atomically: true, encoding: .utf8)
            try FileManager.default.removeItem(atPath: testPath)
            return true // Should not be able to write here
        } catch {
            return false // Cannot write, device is safe
        }
    }

    // MARK: - Handle Jailbroken Device

    static func handleJailbrokenDevice() {
        guard isJailbroken() else { return }

        // Option 1: Show warning and continue
        let alert = UIAlertController(
            title: "Security Warning",
            message: "Your device appears to be jailbroken. Some features may not work correctly.",
            preferredStyle: .alert
        )
        alert.addAction(UIAlertAction(title: "OK", style: .default))

        // Option 2: Exit app (more aggressive)
        // exit(0)

        // Option 3: Disable sensitive features
        // UserDefaults.standard.set(true, forKey: "isJailbroken")
    }
}

// Usage in AppDelegate
func application(_ application: UIApplication, didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {

    if JailbreakDetection.isJailbroken() {
        JailbreakDetection.handleJailbrokenDevice()
    }

    return true
}
```

## Android Security Implementation

### Secure Data Storage (Kotlin)

```kotlin
// SecureStorage.kt - Using Android Keystore
import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec

class SecureStorage(context: Context) {

    // Use EncryptedSharedPreferences for simple key-value storage
    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        MasterKey.Builder(context)
            .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
            .build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    // MARK: - Save/Load with EncryptedSharedPreferences

    fun saveString(key: String, value: String) {
        sharedPreferences.edit().putString(key, value).apply()
    }

    fun loadString(key: String): String? {
        return sharedPreferences.getString(key, null)
    }

    fun delete(key: String) {
        sharedPreferences.edit().remove(key).apply()
    }

    // MARK: - Advanced: Android Keystore Encryption

    companion object {
        private const val KEYSTORE_ALIAS = "SecureStorageKey"
        private const val ANDROID_KEYSTORE = "AndroidKeyStore"
        private const val AES_MODE = "AES/GCM/NoPadding"

        fun encrypt(data: ByteArray): Pair<ByteArray, ByteArray> {
            val cipher = Cipher.getInstance(AES_MODE)
            cipher.init(Cipher.ENCRYPT_MODE, getOrCreateKey())

            val encryptedData = cipher.doFinal(data)
            val iv = cipher.iv

            return Pair(encryptedData, iv)
        }

        fun decrypt(encryptedData: ByteArray, iv: ByteArray): ByteArray {
            val cipher = Cipher.getInstance(AES_MODE)
            val spec = GCMParameterSpec(128, iv)
            cipher.init(Cipher.DECRYPT_MODE, getOrCreateKey(), spec)

            return cipher.doFinal(encryptedData)
        }

        private fun getOrCreateKey(): SecretKey {
            val keyStore = KeyStore.getInstance(ANDROID_KEYSTORE)
            keyStore.load(null)

            if (!keyStore.containsAlias(KEYSTORE_ALIAS)) {
                val keyGenerator = KeyGenerator.getInstance(
                    KeyProperties.KEY_ALGORITHM_AES,
                    ANDROID_KEYSTORE
                )

                val keySpec = KeyGenParameterSpec.Builder(
                    KEYSTORE_ALIAS,
                    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
                )
                    .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
                    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                    .setUserAuthenticationRequired(false) // Set to true for biometric
                    .build()

                keyGenerator.init(keySpec)
                keyGenerator.generateKey()
            }

            return keyStore.getKey(KEYSTORE_ALIAS, null) as SecretKey
        }
    }
}

// Usage
val secureStorage = SecureStorage(context)
secureStorage.saveString("authToken", "sensitive_token_here")
val token = secureStorage.loadString("authToken")
```

### Certificate Pinning (Kotlin + OkHttp)

```kotlin
// NetworkClient.kt
import okhttp3.CertificatePinner
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit

object NetworkClient {

    private const val BASE_URL = "https://api.yourdomain.com/"

    // Certificate pinning configuration
    private val certificatePinner = CertificatePinner.Builder()
        .add("api.yourdomain.com", "sha256/AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=") // Your certificate hash
        .add("api.yourdomain.com", "sha256/BBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBBB=") // Backup certificate
        .build()

    private val okHttpClient = OkHttpClient.Builder()
        .certificatePinner(certificatePinner)
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .addInterceptor { chain ->
            val request = chain.request().newBuilder()
                .addHeader("User-Agent", "YourApp/1.0")
                .build()
            chain.proceed(request)
        }
        .build()

    val retrofit: Retrofit = Retrofit.Builder()
        .baseUrl(BASE_URL)
        .client(okHttpClient)
        .addConverterFactory(GsonConverterFactory.create())
        .build()
}

// Get certificate hash from command line:
// openssl s_client -connect api.yourdomain.com:443 | openssl x509 -pubkey -noout | openssl pkey -pubin -outform der | openssl dgst -sha256 -binary | openssl enc -base64
```

### Biometric Authentication (Kotlin)

```kotlin
// BiometricAuth.kt
import android.content.Context
import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity

class BiometricAuth(private val activity: FragmentActivity) {

    enum class BiometricType {
        FINGERPRINT, FACE, IRIS, NONE
    }

    // MARK: - Check Biometric Availability

    fun checkBiometricSupport(): BiometricType {
        val biometricManager = BiometricManager.from(activity)

        return when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                // Device has biometric capability
                BiometricType.FINGERPRINT // Could be fingerprint, face, or iris
            }
            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE -> BiometricType.NONE
            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE -> BiometricType.NONE
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> BiometricType.NONE
            else -> BiometricType.NONE
        }
    }

    // MARK: - Authenticate

    fun authenticate(
        title: String = "Biometric Authentication",
        subtitle: String = "Authenticate to continue",
        onSuccess: () -> Unit,
        onError: (String) -> Unit
    ) {
        val executor = ContextCompat.getMainExecutor(activity)

        val biometricPrompt = BiometricPrompt(
            activity,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    onSuccess()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    onError(errString.toString())
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    onError("Authentication failed")
                }
            }
        )

        val promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle(title)
            .setSubtitle(subtitle)
            .setNegativeButtonText("Cancel")
            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
            .build()

        biometricPrompt.authenticate(promptInfo)
    }
}

// Usage
val biometricAuth = BiometricAuth(activity)

if (biometricAuth.checkBiometricSupport() != BiometricAuth.BiometricType.NONE) {
    biometricAuth.authenticate(
        title = "Login",
        subtitle = "Authenticate to access your account",
        onSuccess = {
            // Proceed with sensitive operation
        },
        onError = { error ->
            Log.e("BiometricAuth", "Error: $error")
        }
    )
}
```

### Root Detection (Kotlin)

```kotlin
// RootDetection.kt
import android.os.Build
import java.io.File

object RootDetection {

    // MARK: - Check if Device is Rooted

    fun isRooted(): Boolean {
        return checkBuildTags() || checkSuperuserApk() || checkSuBinary() || checkRWPaths()
    }

    // MARK: - Check Build Tags

    private fun checkBuildTags(): Boolean {
        val buildTags = Build.TAGS
        return buildTags != null && buildTags.contains("test-keys")
    }

    // MARK: - Check for Superuser APK

    private fun checkSuperuserApk(): Boolean {
        val paths = arrayOf(
            "/system/app/Superuser.apk",
            "/system/app/SuperSU.apk",
            "/system/app/Kinguser.apk",
            "/data/app/eu.chainfire.supersu",
            "/data/app/com.noshufou.android.su",
            "/data/app/com.koushikdutta.superuser",
            "/data/app/com.thirdparty.superuser",
            "/data/app/com.yellowes.su"
        )

        return paths.any { File(it).exists() }
    }

    // MARK: - Check for SU Binary

    private fun checkSuBinary(): Boolean {
        val paths = arrayOf(
            "/system/bin/su",
            "/system/xbin/su",
            "/system/sbin/su",
            "/sbin/su",
            "/vendor/bin/su",
            "/su/bin/su"
        )

        return paths.any { File(it).exists() }
    }

    // MARK: - Check for RW Paths

    private fun checkRWPaths(): Boolean {
        val paths = arrayOf(
            "/system",
            "/system/bin",
            "/system/sbin",
            "/system/xbin",
            "/vendor/bin",
            "/sbin",
            "/etc"
        )

        return paths.any { canWriteToPath(it) }
    }

    private fun canWriteToPath(path: String): Boolean {
        val file = File(path)
        return file.canWrite()
    }

    // MARK: - Handle Rooted Device

    fun handleRootedDevice() {
        if (isRooted()) {
            // Option 1: Show warning
            // Show dialog to user

            // Option 2: Exit app
            // exitProcess(0)

            // Option 3: Disable sensitive features
            // Disable payment, authentication, etc.
        }
    }
}

// Usage in Application class
class MyApplication : Application() {
    override fun onCreate() {
        super.onCreate()

        if (RootDetection.isRooted()) {
            RootDetection.handleRootedDevice()
        }
    }
}
```

## Security Testing

### Automated Security Scanning

```yaml
# .github/workflows/mobile-security.yml
name: Mobile Security Scan

on:
  pull_request:
    branches: [main]

jobs:
  ios-security:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install MobSF CLI
        run: pip install mobsf

      - name: Build iOS app
        run: xcodebuild -workspace App.xcworkspace -scheme App -configuration Release

      - name: Run MobSF scan
        run: mobsf scan App.ipa

  android-security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Android APK
        run: ./gradlew assembleRelease

      - name: Run MobSF scan
        run: mobsf scan app-release.apk
```

## Best Practices Checklist

- [ ] Encrypt all sensitive data at rest
- [ ] Use platform-specific secure storage (Keychain/Keystore)
- [ ] Implement certificate pinning for API calls
- [ ] Enable biometric authentication for sensitive operations
- [ ] Implement jailbreak/root detection
- [ ] Use TLS 1.3 for all network traffic
- [ ] Validate all server responses
- [ ] Clear sensitive data from memory after use
- [ ] Implement auto-lock after inactivity
- [ ] Use secure random number generation
- [ ] Obfuscate code in production builds
- [ ] Implement anti-debugging measures
- [ ] Validate deep links and intent data
- [ ] Never log sensitive information
- [ ] Regularly update dependencies

## Related Resources

- [OWASP Mobile Security Testing Guide](https://owasp.org/www-project-mobile-security-testing-guide/)
- [OWASP MASVS](https://github.com/OWASP/owasp-masvs)
- [iOS Security Guide](https://support.apple.com/guide/security/welcome/web)
- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)
