# Android App Template (Kotlin + Jetpack Compose)

Complete production-ready Android application template using Kotlin, Jetpack Compose, MVVM architecture, Retrofit for networking, Room for persistence, and modern Android patterns.

---

## Tech Stack

- **Language**: Kotlin 2.0+
- **UI Framework**: Jetpack Compose
- **Architecture**: MVVM (Model-View-Intent)
- **Networking**: Retrofit + OkHttp + Coroutines
- **Persistence**: Room
- **Navigation**: Jetpack Navigation Compose
- **Dependency Injection**: Hilt
- **Authentication**: EncryptedSharedPreferences
- **Testing**: JUnit, MockK, Espresso
- **Build**: Gradle (Kotlin DSL)

---

## Project Structure

```
app/
├── src/
│   ├── main/
│   │   ├── java/com/example/yourapp/
│   │   │   ├── YourApp.kt             # Application class
│   │   │   ├── MainActivity.kt        # Main activity
│   │   │   ├── di/                    # Dependency injection
│   │   │   │   ├── AppModule.kt
│   │   │   │   └── NetworkModule.kt
│   │   │   ├── data/
│   │   │   │   ├── local/
│   │   │   │   │   ├── dao/
│   │   │   │   │   │   └── UserDao.kt
│   │   │   │   │   ├── entities/
│   │   │   │   │   │   └── UserEntity.kt
│   │   │   │   │   └── AppDatabase.kt
│   │   │   │   ├── remote/
│   │   │   │   │   ├── api/
│   │   │   │   │   │   └── ApiService.kt
│   │   │   │   │   └── dto/
│   │   │   │   │       ├── UserDto.kt
│   │   │   │   │       └── PostDto.kt
│   │   │   │   └── repository/
│   │   │   │       ├── AuthRepository.kt
│   │   │   │       └── UserRepository.kt
│   │   │   ├── domain/
│   │   │   │   └── model/
│   │   │   │       ├── User.kt
│   │   │   │       └── Post.kt
│   │   │   ├── presentation/
│   │   │   │   ├── auth/
│   │   │   │   │   ├── LoginScreen.kt
│   │   │   │   │   ├── LoginViewModel.kt
│   │   │   │   │   └── RegisterScreen.kt
│   │   │   │   ├── users/
│   │   │   │   │   ├── UsersScreen.kt
│   │   │   │   │   ├── UsersViewModel.kt
│   │   │   │   │   └── UserDetailScreen.kt
│   │   │   │   ├── components/
│   │   │   │   │   ├── LoadingView.kt
│   │   │   │   │   └── ErrorView.kt
│   │   │   │   └── navigation/
│   │   │   │       └── AppNavigation.kt
│   │   │   └── util/
│   │   │       ├── SecureStorage.kt
│   │   │       ├── Constants.kt
│   │   │       └── Extensions.kt
│   │   └── AndroidManifest.xml
│   └── test/
│       └── java/com/example/yourapp/
└── build.gradle.kts
```

---

## 1. App Configuration

**app/build.gradle.kts**
```kotlin
plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("kotlin-kapt")
    id("com.google.dagger.hilt.android")
}

android {
    namespace = "com.example.yourapp"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.yourapp"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        vectorDrawables {
            useSupportLibrary = true
        }
    }

    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    buildFeatures {
        compose = true
    }

    composeOptions {
        kotlinCompilerExtensionVersion = "1.5.3"
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    // Compose
    implementation("androidx.compose.ui:ui:1.5.4")
    implementation("androidx.compose.material3:material3:1.1.2")
    implementation("androidx.compose.ui:ui-tooling-preview:1.5.4")
    implementation("androidx.activity:activity-compose:1.8.1")

    // Navigation
    implementation("androidx.navigation:navigation-compose:2.7.5")

    // ViewModel
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.6.2")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.6.2")

    // Coroutines
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")

    // Retrofit
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")
    implementation("com.squareup.okhttp3:okhttp:4.12.0")
    implementation("com.squareup.okhttp3:logging-interceptor:4.12.0")

    // Room
    implementation("androidx.room:room-runtime:2.6.1")
    implementation("androidx.room:room-ktx:2.6.1")
    kapt("androidx.room:room-compiler:2.6.1")

    // Hilt
    implementation("com.google.dagger:hilt-android:2.48.1")
    kapt("com.google.dagger:hilt-compiler:2.48.1")
    implementation("androidx.hilt:hilt-navigation-compose:1.1.0")

    // Security
    implementation("androidx.security:security-crypto:1.1.0-alpha06")

    // Testing
    testImplementation("junit:junit:4.13.2")
    testImplementation("io.mockk:mockk:1.13.8")
    testImplementation("org.jetbrains.kotlinx:kotlinx-coroutines-test:1.7.3")
    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")
    androidTestImplementation("androidx.compose.ui:ui-test-junit4:1.5.4")
    debugImplementation("androidx.compose.ui:ui-tooling:1.5.4")
}
```

---

## 2. Application Class

**YourApp.kt**
```kotlin
package com.example.yourapp

import android.app.Application
import dagger.hilt.android.HiltAndroidApp

@HiltAndroidApp
class YourApp : Application()
```

**AndroidManifest.xml**
```xml
<application
    android:name=".YourApp"
    android:allowBackup="true"
    android:icon="@mipmap/ic_launcher"
    android:label="@string/app_name"
    android:theme="@style/Theme.YourApp"
    android:usesCleartextTraffic="false">

    <activity
        android:name=".MainActivity"
        android:exported="true"
        android:theme="@style/Theme.YourApp">
        <intent-filter>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent-filter>
    </activity>
</application>
```

---

## 3. Data Layer

**data/remote/dto/UserDto.kt**
```kotlin
package com.example.yourapp.data.remote.dto

import com.google.gson.annotations.SerializedName

data class UserDto(
    val id: String,
    val email: String,
    val name: String,
    @SerializedName("created_at")
    val createdAt: String
)

data class CreateUserRequest(
    val email: String,
    val password: String,
    val name: String
)

data class LoginRequest(
    val email: String,
    val password: String
)

data class AuthResponse(
    val token: String,
    val user: UserDto
)
```

**data/remote/dto/PostDto.kt**
```kotlin
package com.example.yourapp.data.remote.dto

import com.google.gson.annotations.SerializedName

data class PostDto(
    val id: String,
    val title: String,
    val content: String,
    @SerializedName("author_id")
    val authorId: String,
    @SerializedName("created_at")
    val createdAt: String
)

data class CreatePostRequest(
    val title: String,
    val content: String
)

data class PaginatedResponse<T>(
    val data: List<T>,
    val total: Int,
    val page: Int,
    @SerializedName("page_size")
    val pageSize: Int
)
```

**data/remote/api/ApiService.kt**
```kotlin
package com.example.yourapp.data.remote.api

import com.example.yourapp.data.remote.dto.*
import retrofit2.http.*

interface ApiService {
    @POST("auth/login")
    suspend fun login(@Body request: LoginRequest): AuthResponse

    @POST("auth/register")
    suspend fun register(@Body request: CreateUserRequest): AuthResponse

    @GET("users")
    suspend fun getUsers(): List<UserDto>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") id: String): UserDto

    @GET("posts")
    suspend fun getPosts(
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20
    ): PaginatedResponse<PostDto>

    @POST("posts")
    suspend fun createPost(@Body post: CreatePostRequest): PostDto

    @PUT("posts/{id}")
    suspend fun updatePost(
        @Path("id") id: String,
        @Body post: CreatePostRequest
    ): PostDto

    @DELETE("posts/{id}")
    suspend fun deletePost(@Path("id") id: String)
}
```

**data/local/entities/UserEntity.kt**
```kotlin
package com.example.yourapp.data.local.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey val id: String,
    val email: String,
    val name: String,
    val createdAt: Long
)
```

**data/local/dao/UserDao.kt**
```kotlin
package com.example.yourapp.data.local.dao

import androidx.room.*
import com.example.yourapp.data.local.entities.UserEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface UserDao {
    @Query("SELECT * FROM users")
    fun getAll(): Flow<List<UserEntity>>

    @Query("SELECT * FROM users WHERE id = :id")
    suspend fun getById(id: String): UserEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Update
    suspend fun update(user: UserEntity)

    @Delete
    suspend fun delete(user: UserEntity)

    @Query("DELETE FROM users")
    suspend fun deleteAll()
}
```

**data/local/AppDatabase.kt**
```kotlin
package com.example.yourapp.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import com.example.yourapp.data.local.dao.UserDao
import com.example.yourapp.data.local.entities.UserEntity

@Database(entities = [UserEntity::class], version = 1, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
}
```

**data/repository/AuthRepository.kt**
```kotlin
package com.example.yourapp.data.repository

import com.example.yourapp.data.remote.api.ApiService
import com.example.yourapp.data.remote.dto.AuthResponse
import com.example.yourapp.data.remote.dto.CreateUserRequest
import com.example.yourapp.data.remote.dto.LoginRequest
import com.example.yourapp.util.SecureStorage
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class AuthRepository @Inject constructor(
    private val apiService: ApiService,
    private val secureStorage: SecureStorage
) {
    suspend fun login(email: String, password: String): Result<AuthResponse> {
        return try {
            val response = apiService.login(LoginRequest(email, password))
            secureStorage.saveToken(response.token)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    suspend fun register(email: String, password: String, name: String): Result<AuthResponse> {
        return try {
            val response = apiService.register(CreateUserRequest(email, password, name))
            secureStorage.saveToken(response.token)
            Result.success(response)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }

    fun logout() {
        secureStorage.clearToken()
    }

    fun getToken(): String? = secureStorage.getToken()

    fun isAuthenticated(): Boolean = getToken() != null
}
```

---

## 4. Dependency Injection

**di/NetworkModule.kt**
```kotlin
package com.example.yourapp.di

import com.example.yourapp.data.remote.api.ApiService
import com.example.yourapp.util.SecureStorage
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(secureStorage: SecureStorage): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor { chain ->
                val request = chain.request().newBuilder()
                secureStorage.getToken()?.let { token ->
                    request.addHeader("Authorization", "Bearer $token")
                }
                chain.proceed(request.build())
            }
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .build()
    }

    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService {
        return retrofit.create(ApiService::class.java)
    }
}
```

**di/AppModule.kt**
```kotlin
package com.example.yourapp.di

import android.content.Context
import androidx.room.Room
import com.example.yourapp.data.local.AppDatabase
import com.example.yourapp.data.local.dao.UserDao
import com.example.yourapp.util.SecureStorage
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun provideAppDatabase(@ApplicationContext context: Context): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            "app_database"
        ).build()
    }

    @Provides
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }

    @Provides
    @Singleton
    fun provideSecureStorage(@ApplicationContext context: Context): SecureStorage {
        return SecureStorage(context)
    }
}
```

---

## 5. Presentation Layer

**presentation/auth/LoginViewModel.kt**
```kotlin
package com.example.yourapp.presentation.auth

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.yourapp.data.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

data class LoginUiState(
    val isLoading: Boolean = false,
    val isAuthenticated: Boolean = false,
    val errorMessage: String? = null
)

@HiltViewModel
class LoginViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(LoginUiState())
    val uiState = _uiState.asStateFlow()

    init {
        checkAuthStatus()
    }

    private fun checkAuthStatus() {
        _uiState.value = _uiState.value.copy(
            isAuthenticated = authRepository.isAuthenticated()
        )
    }

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

            authRepository.login(email, password)
                .onSuccess {
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        isAuthenticated = true
                    )
                }
                .onFailure { error ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        errorMessage = error.message ?: "Login failed"
                    )
                }
        }
    }

    fun logout() {
        authRepository.logout()
        _uiState.value = _uiState.value.copy(isAuthenticated = false)
    }
}
```

**presentation/auth/LoginScreen.kt**
```kotlin
package com.example.yourapp.presentation.auth

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun LoginScreen(
    onNavigateToRegister: () -> Unit,
    onLoginSuccess: () -> Unit,
    viewModel: LoginViewModel = hiltViewModel()
) {
    val uiState by viewModel.uiState.collectAsState()
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    LaunchedEffect(uiState.isAuthenticated) {
        if (uiState.isAuthenticated) {
            onLoginSuccess()
        }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Welcome Back",
            style = MaterialTheme.typography.headlineLarge
        )

        Spacer(modifier = Modifier.height(32.dp))

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )

        Spacer(modifier = Modifier.height(16.dp))

        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            modifier = Modifier.fillMaxWidth(),
            singleLine = true,
            visualTransformation = PasswordVisualTransformation()
        )

        uiState.errorMessage?.let { error ->
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = error,
                color = MaterialTheme.colorScheme.error,
                style = MaterialTheme.typography.bodySmall
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        Button(
            onClick = { viewModel.login(email, password) },
            modifier = Modifier.fillMaxWidth(),
            enabled = !uiState.isLoading && email.isNotBlank() && password.isNotBlank()
        ) {
            if (uiState.isLoading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text("Sign In")
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        TextButton(onClick = onNavigateToRegister) {
            Text("Create Account")
        }
    }
}
```

---

## 6. Utilities

**util/SecureStorage.kt**
```kotlin
package com.example.yourapp.util

import android.content.Context
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey

class SecureStorage(context: Context) {
    private val masterKey = MasterKey.Builder(context)
        .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
        .build()

    private val sharedPreferences = EncryptedSharedPreferences.create(
        context,
        "secure_prefs",
        masterKey,
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
    )

    fun saveToken(token: String) {
        sharedPreferences.edit()
            .putString("auth_token", token)
            .apply()
    }

    fun getToken(): String? {
        return sharedPreferences.getString("auth_token", null)
    }

    fun clearToken() {
        sharedPreferences.edit()
            .remove("auth_token")
            .apply()
    }
}
```

---

## 7. Testing

**LoginViewModelTest.kt**
```kotlin
package com.example.yourapp.presentation.auth

import com.example.yourapp.data.repository.AuthRepository
import io.mockk.coEvery
import io.mockk.mockk
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.*
import org.junit.After
import org.junit.Before
import org.junit.Test
import kotlin.test.assertFalse
import kotlin.test.assertTrue

@OptIn(ExperimentalCoroutinesApi::class)
class LoginViewModelTest {
    private val testDispatcher = StandardTestDispatcher()
    private lateinit var authRepository: AuthRepository
    private lateinit var viewModel: LoginViewModel

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        authRepository = mockk()
        viewModel = LoginViewModel(authRepository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `login success updates UI state`() = runTest {
        coEvery { authRepository.login(any(), any()) } returns Result.success(mockk())

        viewModel.login("test@example.com", "password")
        testDispatcher.scheduler.advanceUntilIdle()

        assertFalse(viewModel.uiState.value.isLoading)
        assertTrue(viewModel.uiState.value.isAuthenticated)
    }
}
```

---

## Best Practices

1. **Architecture**: Use MVVM with clean architecture layers
2. **Coroutines**: Use viewModelScope for lifecycle-aware operations
3. **State**: Use StateFlow for reactive UI updates
4. **Security**: Encrypt sensitive data with EncryptedSharedPreferences
5. **DI**: Use Hilt for dependency injection
6. **Testing**: Write unit tests for ViewModels and repositories

---

This template provides a solid foundation for building production-ready Android applications with modern Kotlin and Jetpack Compose patterns.
