# Jetpack Compose Advanced Patterns Reference

Comprehensive guide to advanced Jetpack Compose patterns including custom modifiers, side effects, animations, and Kotlin-specific features for building sophisticated Android UIs.

---

## Table of Contents

1. [Custom Modifiers](#custom-modifiers)
2. [Side Effects](#side-effects)
3. [State Hoisting & Delegation](#state-hoisting--delegation)
4. [Advanced Animations](#advanced-animations)
5. [Performance Optimization](#performance-optimization)

---

## Custom Modifiers

**Use when:** Creating reusable UI styling and behavior.

### Custom Modifier

```kotlin
fun Modifier.cardStyle(
    backgroundColor: Color = MaterialTheme.colorScheme.surface,
    cornerRadius: Dp = 12.dp,
    elevation: Dp = 4.dp
): Modifier = this
    .shadow(elevation, RoundedCornerShape(cornerRadius))
    .background(backgroundColor, RoundedCornerShape(cornerRadius))
    .padding(16.dp)

// Usage
Text(
    text = "Hello, World!",
    modifier = Modifier.cardStyle()
)

Column(
    modifier = Modifier
        .fillMaxWidth()
        .cardStyle(
            backgroundColor = MaterialTheme.colorScheme.primaryContainer,
            cornerRadius = 16.dp
        )
) {
    Text("Custom Card")
}
```

### Conditional Modifier

```kotlin
fun Modifier.conditional(
    condition: Boolean,
    modifier: Modifier.() -> Modifier
): Modifier = if (condition) {
    then(modifier(Modifier))
} else {
    this
}

// Usage
Text(
    text = "Conditional Styling",
    modifier = Modifier
        .conditional(isHighlighted) {
            background(Color.Yellow)
                .border(2.dp, Color.Red)
        }
)
```

### Modifier with Parameters

```kotlin
fun Modifier.shimmer(
    isLoading: Boolean,
    shimmerColor: Color = Color.LightGray.copy(alpha = 0.6f)
): Modifier = composed {
    if (!isLoading) return@composed this

    val transition = rememberInfiniteTransition(label = "shimmer")
    val translateAnim by transition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 1200, easing = FastOutSlowInEasing),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer_translate"
    )

    background(
        brush = Brush.linearGradient(
            colors = listOf(
                shimmerColor.copy(alpha = 0.6f),
                shimmerColor.copy(alpha = 0.2f),
                shimmerColor.copy(alpha = 0.6f)
            ),
            start = Offset(translateAnim, 0f),
            end = Offset(translateAnim + 200f, 0f)
        )
    )
}

// Usage
Box(
    modifier = Modifier
        .size(200.dp, 20.dp)
        .shimmer(isLoading = true)
)
```

**Checklist:**
- [ ] Extract repeated styling into custom modifiers
- [ ] Use `composed` for stateful modifiers
- [ ] Keep modifiers composable and reusable
- [ ] Document modifier parameters
- [ ] Use conditional logic for dynamic styling

---

## Side Effects

**Use when:** Performing side effects in composables that sync with Compose lifecycle.

### LaunchedEffect

```kotlin
@Composable
fun UserScreen(userId: String, viewModel: UserViewModel) {
    LaunchedEffect(userId) {
        // Runs when userId changes
        viewModel.loadUser(userId)
    }

    // UI code
}

// One-time effect
@Composable
fun AnalyticsScreen(screenName: String) {
    LaunchedEffect(Unit) {
        // Runs once when composable enters composition
        analyticsService.logScreenView(screenName)
    }
}
```

### DisposableEffect

```kotlin
@Composable
fun BackPressHandler(onBackPressed: () -> Unit) {
    val context = LocalContext.current
    val backCallback = remember {
        object : OnBackPressedCallback(true) {
            override fun handleOnBackPressed() {
                onBackPressed()
            }
        }
    }

    DisposableEffect(context) {
        val activity = context as? ComponentActivity
        activity?.onBackPressedDispatcher?.addCallback(backCallback)

        onDispose {
            backCallback.remove()
        }
    }
}
```

### SideEffect

```kotlin
@Composable
fun SystemBarsTheme(isDark: Boolean) {
    val view = LocalView.current

    SideEffect {
        // Runs after every successful recomposition
        val window = (view.context as Activity).window
        window.statusBarColor = if (isDark) Color.Black else Color.White
    }
}
```

### rememberCoroutineScope

```kotlin
@Composable
fun SwipeableContent() {
    val scope = rememberCoroutineScope()
    val scaffoldState = rememberScaffoldState()

    Scaffold(
        scaffoldState = scaffoldState
    ) {
        Button(
            onClick = {
                scope.launch {
                    scaffoldState.snackbarHostState.showSnackbar("Hello!")
                }
            }
        ) {
            Text("Show Snackbar")
        }
    }
}
```

### derivedStateOf

```kotlin
@Composable
fun ItemList(items: List<Item>) {
    val listState = rememberLazyListState()

    // Only recomputes when first visible item changes
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    Box {
        LazyColumn(state = listState) {
            items(items) { item ->
                ItemRow(item)
            }
        }

        AnimatedVisibility(visible = showButton) {
            FloatingActionButton(
                onClick = {
                    // Scroll to top
                }
            ) {
                Icon(Icons.Default.ArrowUpward, null)
            }
        }
    }
}
```

**Checklist:**
- [ ] Use LaunchedEffect for coroutines tied to keys
- [ ] Use DisposableEffect for cleanup
- [ ] Use SideEffect for synchronizing non-Compose state
- [ ] Use derivedStateOf for computed state
- [ ] Use rememberCoroutineScope for event handlers

---

## State Hoisting & Delegation

**Use when:** Managing state in composable hierarchies.

### State Hoisting Pattern

```kotlin
// Stateless composable
@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = query,
        onValueChange = onQueryChange,
        modifier = modifier,
        placeholder = { Text("Search") }
    )
}

// Stateful composable
@Composable
fun SearchScreen() {
    var query by remember { mutableStateOf("") }

    Column {
        SearchBar(
            query = query,
            onQueryChange = { query = it }
        )

        SearchResults(query)
    }
}
```

### Remember with Custom Key

```kotlin
@Composable
fun UserProfile(userId: String) {
    // Resets when userId changes
    val userData by remember(userId) {
        mutableStateOf(UserData())
    }

    LaunchedEffect(userId) {
        // Load new user data
    }
}
```

### rememberSaveable for Configuration Changes

```kotlin
@Composable
fun FormScreen() {
    var name by rememberSaveable { mutableStateOf("") }
    var email by rememberSaveable { mutableStateOf("") }

    // State survives configuration changes (rotation)
    Column {
        OutlinedTextField(
            value = name,
            onValueChange = { name = it },
            label = { Text("Name") }
        )

        OutlinedTextField(
            value = email,
            onValueChange = { email = it },
            label = { Text("Email") }
        )
    }
}
```

### State Delegate

```kotlin
class SearchState {
    var query by mutableStateOf("")
        private set

    var results by mutableStateOf<List<Result>>(emptyList())
        private set

    var isLoading by mutableStateOf(false)
        private set

    fun updateQuery(newQuery: String) {
        query = newQuery
    }

    fun updateResults(newResults: List<Result>) {
        results = newResults
        isLoading = false
    }
}

@Composable
fun rememberSearchState() = remember { SearchState() }

@Composable
fun SearchScreen() {
    val searchState = rememberSearchState()

    Column {
        SearchBar(
            query = searchState.query,
            onQueryChange = searchState::updateQuery
        )

        if (searchState.isLoading) {
            CircularProgressIndicator()
        } else {
            SearchResults(searchState.results)
        }
    }
}
```

**Checklist:**
- [ ] Hoist state to appropriate level
- [ ] Make composables stateless when possible
- [ ] Use remember for state that doesn't survive config changes
- [ ] Use rememberSaveable for state that should survive
- [ ] Create state holders for complex state logic

---

## Advanced Animations

**Use when:** Creating smooth, interactive animations.

### AnimatedVisibility

```kotlin
@Composable
fun ExpandableCard() {
    var expanded by remember { mutableStateOf(false) }

    Card {
        Column {
            Row(
                modifier = Modifier.clickable { expanded = !expanded }
            ) {
                Text("Card Title")
                Icon(
                    imageVector = if (expanded) Icons.Default.ExpandLess else Icons.Default.ExpandMore,
                    contentDescription = null
                )
            }

            AnimatedVisibility(
                visible = expanded,
                enter = fadeIn() + expandVertically(),
                exit = fadeOut() + shrinkVertically()
            ) {
                Text(
                    "Card content that appears and disappears with animation",
                    modifier = Modifier.padding(16.dp)
                )
            }
        }
    }
}
```

### Animated Content Size

```kotlin
@Composable
fun DynamicContent() {
    var showMore by remember { mutableStateOf(false) }

    Column(
        modifier = Modifier.animateContentSize(
            animationSpec = spring(
                dampingRatio = Spring.DampingRatioMediumBouncy,
                stiffness = Spring.StiffnessLow
            )
        )
    ) {
        Text("Always visible content")

        if (showMore) {
            Text("Additional content with animated height")
        }

        TextButton(onClick = { showMore = !showMore }) {
            Text(if (showMore) "Show Less" else "Show More")
        }
    }
}
```

### Animated Value

```kotlin
@Composable
fun ProgressIndicator(progress: Float) {
    val animatedProgress by animateFloatAsState(
        targetValue = progress,
        animationSpec = tween(durationMillis = 1000, easing = EaseInOutCubic),
        label = "progress"
    )

    LinearProgressIndicator(
        progress = animatedProgress,
        modifier = Modifier.fillMaxWidth()
    )
}
```

### Transition Animation

```kotlin
enum class BoxState { Collapsed, Expanded }

@Composable
fun AnimatedBox() {
    var currentState by remember { mutableStateOf(BoxState.Collapsed) }
    val transition = updateTransition(currentState, label = "box")

    val size by transition.animateDp(
        label = "size",
        transitionSpec = { spring(stiffness = Spring.StiffnessLow) }
    ) { state ->
        when (state) {
            BoxState.Collapsed -> 64.dp
            BoxState.Expanded -> 128.dp
        }
    }

    val color by transition.animateColor(
        label = "color"
    ) { state ->
        when (state) {
            BoxState.Collapsed -> MaterialTheme.colorScheme.primary
            BoxState.Expanded -> MaterialTheme.colorScheme.secondary
        }
    }

    Box(
        modifier = Modifier
            .size(size)
            .background(color)
            .clickable {
                currentState = when (currentState) {
                    BoxState.Collapsed -> BoxState.Expanded
                    BoxState.Expanded -> BoxState.Collapsed
                }
            }
    )
}
```

### Infinite Animation

```kotlin
@Composable
fun PulsingIcon() {
    val infiniteTransition = rememberInfiniteTransition(label = "pulse")
    val scale by infiniteTransition.animateFloat(
        initialValue = 1f,
        targetValue = 1.2f,
        animationSpec = infiniteRepeatable(
            animation = tween(800),
            repeatMode = RepeatMode.Reverse
        ),
        label = "scale"
    )

    Icon(
        imageVector = Icons.Default.Favorite,
        contentDescription = null,
        modifier = Modifier.scale(scale)
    )
}
```

**Checklist:**
- [ ] Use AnimatedVisibility for enter/exit animations
- [ ] Use animateContentSize for size changes
- [ ] Use animate*AsState for simple value animations
- [ ] Use Transition for coordinated animations
- [ ] Use InfiniteTransition for continuous animations

---

## Performance Optimization

**Use when:** Optimizing recomposition and rendering performance.

### Remember Expensive Computations

```kotlin
@Composable
fun ExpensiveList(items: List<Item>) {
    // Avoid recomputing on every recomposition
    val processedItems = remember(items) {
        items.map { processItem(it) }
    }

    LazyColumn {
        items(processedItems) { item ->
            ItemRow(item)
        }
    }
}
```

### Key for LazyColumn Items

```kotlin
@Composable
fun ItemList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            key = { item -> item.id } // Helps Compose identify items
        ) { item ->
            ItemRow(item)
        }
    }
}
```

### Stable Collections

```kotlin
// Immutable collections prevent unnecessary recompositions
@Immutable
data class UserList(val users: List<User>)

// Or use kotlinx.collections.immutable
import kotlinx.collections.immutable.ImmutableList
import kotlinx.collections.immutable.persistentListOf

@Composable
fun UserScreen(users: ImmutableList<User>) {
    // Compose knows this won't change unless reference changes
    LazyColumn {
        items(users) { user ->
            UserRow(user)
        }
    }
}
```

### Skip Recomposition with Stability

```kotlin
// Unstable class - recomposes every time
data class SearchQuery(var text: String)

// Stable class - only recomposes when text changes
@Stable
data class SearchQuery(val text: String)

// Or make it immutable
data class SearchQuery(val text: String) {
    fun update(newText: String) = copy(text = newText)
}
```

### Avoid Allocation in Composition

```kotlin
// Bad - creates new lambda on every recomposition
@Composable
fun Button() {
    Button(onClick = { viewModel.doSomething() }) {
        Text("Click")
    }
}

// Good - lambda is stable
@Composable
fun Button(viewModel: ViewModel) {
    Button(onClick = viewModel::doSomething) {
        Text("Click")
    }
}
```

### Defer State Reads

```kotlin
@Composable
fun ScrollToTopButton(listState: LazyListState) {
    val scope = rememberCoroutineScope()

    // Bad - reads state in composition phase
    val showButton = listState.firstVisibleItemIndex > 0

    // Good - defers state read
    val showButton by remember {
        derivedStateOf {
            listState.firstVisibleItemIndex > 0
        }
    }

    AnimatedVisibility(visible = showButton) {
        FloatingActionButton(
            onClick = {
                scope.launch {
                    listState.animateScrollToItem(0)
                }
            }
        ) {
            Icon(Icons.Default.ArrowUpward, null)
        }
    }
}
```

**Checklist:**
- [ ] Use `remember` for expensive computations
- [ ] Provide `key` for lazy list items
- [ ] Use immutable/stable data classes
- [ ] Avoid allocations in composition
- [ ] Use `derivedStateOf` for computed values
- [ ] Profile with Layout Inspector

---

## Best Practices

1. **Modifiers**
   - Keep custom modifiers focused and reusable
   - Use `composed` for stateful modifiers
   - Document modifier behavior and parameters
   - Chain modifiers in logical order

2. **Side Effects**
   - Use the right effect for the job
   - Clean up resources in onDispose
   - Avoid long-running work in composition
   - Use remember for state initialization

3. **State Management**
   - Hoist state to appropriate level
   - Make composables stateless when possible
   - Use state holders for complex state
   - Preserve state across configuration changes

4. **Animations**
   - Use built-in animation APIs
   - Coordinate related animations with Transition
   - Use appropriate easing functions
   - Test animations on real devices

5. **Performance**
   - Minimize recompositions
   - Use stable/immutable data
   - Provide keys for lists
   - Defer expensive computations
   - Profile with tools

---

This reference provides advanced Jetpack Compose patterns for building sophisticated, production-ready Android user interfaces.
