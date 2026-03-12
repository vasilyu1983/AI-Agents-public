# Material-UI (MUI) Component Library Template

Material-UI (MUI) is the most popular React UI library with 95k+ GitHub stars and 4.1M+ weekly downloads. It implements Google's Material Design system with a comprehensive set of pre-built, customizable React components for building modern web applications.

---

## Key Characteristics

**Architecture**: Full-featured NPM package with extensive component library
**Styling**: Emotion-based CSS-in-JS with sx prop and styled API
**Design System**: Google Material Design 3 (M3) principles
**TypeScript**: Complete TypeScript support with strict types
**Customization**: Theme customization via theme provider
**Accessibility**: Strong a11y defaults; verify WCAG 2.2 AA at the app level

**Best for**:
- Enterprise applications
- Teams familiar with Material Design
- Projects requiring comprehensive out-of-the-box components
- Rapid prototyping with minimal custom styling

**Trusted by**: Spotify, Amazon, Netflix, NASA, Unity

---

## Installation & Setup

### Core Package
```bash
npm install @mui/material @emotion/react @emotion/styled
```

### Optional Packages
```bash
# Icons
npm install @mui/icons-material

# Data Grid (advanced tables)
npm install @mui/x-data-grid

# Date pickers
npm install @mui/x-date-pickers dayjs

# Charts
npm install @mui/x-charts
```

### Font Setup
```html
<!-- Add to <head> in your HTML -->
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
/>
<link
  rel="stylesheet"
  href="https://fonts.googleapis.com/icon?family=Material+Icons"
/>
```

---

## Project Structure

```
src/
├── components/
│   ├── common/          # Reusable MUI-wrapped components
│   ├── layouts/         # Page layouts
│   └── pages/           # Page components
├── theme/
│   ├── theme.ts         # MUI theme configuration
│   └── overrides.ts     # Component style overrides
├── App.tsx
└── index.tsx
```

---

## Theme Configuration

### Basic Theme Setup

```tsx
// theme/theme.ts
import { createTheme } from '@mui/material/styles'

export const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
      light: '#42a5f5',
      dark: '#1565c0',
      contrastText: '#fff',
    },
    secondary: {
      main: '#9c27b0',
      light: '#ba68c8',
      dark: '#7b1fa2',
      contrastText: '#fff',
    },
    error: {
      main: '#d32f2f',
    },
    warning: {
      main: '#ed6c02',
    },
    info: {
      main: '#0288d1',
    },
    success: {
      main: '#2e7d32',
    },
  },
  typography: {
    fontFamily: [
      'Roboto',
      '-apple-system',
      'BlinkMacSystemFont',
      '"Segoe UI"',
      'Arial',
      'sans-serif',
    ].join(','),
    h1: {
      fontSize: '2.5rem',
      fontWeight: 500,
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
      lineHeight: 1.5,
    },
  },
  spacing: 8, // Default spacing unit (8px)
  shape: {
    borderRadius: 4, // Default border radius
  },
})

// App.tsx
import { ThemeProvider } from '@mui/material/styles'
import CssBaseline from '@mui/material/CssBaseline'
import { theme } from './theme/theme'

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {/* Your app content */}
    </ThemeProvider>
  )
}
```

### Dark Mode Support

```tsx
import { useState, useMemo } from 'react'
import { createTheme, ThemeProvider } from '@mui/material/styles'
import { PaletteMode } from '@mui/material'
import CssBaseline from '@mui/material/CssBaseline'
import IconButton from '@mui/material/IconButton'
import Brightness4Icon from '@mui/icons-material/Brightness4'
import Brightness7Icon from '@mui/icons-material/Brightness7'

function App() {
  const [mode, setMode] = useState<PaletteMode>('light')

  const theme = useMemo(
    () =>
      createTheme({
        palette: {
          mode,
          ...(mode === 'light'
            ? {
                // Light mode colors
                primary: { main: '#1976d2' },
                background: { default: '#fff', paper: '#f5f5f5' },
              }
            : {
                // Dark mode colors
                primary: { main: '#90caf9' },
                background: { default: '#121212', paper: '#1e1e1e' },
              }),
        },
      }),
    [mode]
  )

  const toggleColorMode = () => {
    setMode((prevMode) => (prevMode === 'light' ? 'dark' : 'light'))
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <IconButton onClick={toggleColorMode} color="inherit">
        {mode === 'dark' ? <Brightness7Icon /> : <Brightness4Icon />}
      </IconButton>
      {/* Your app content */}
    </ThemeProvider>
  )
}
```

---

## Core Components Usage

### Buttons

```tsx
import Button from '@mui/material/Button'
import IconButton from '@mui/material/IconButton'
import DeleteIcon from '@mui/icons-material/Delete'
import LoadingButton from '@mui/lab/LoadingButton'
import SaveIcon from '@mui/icons-material/Save'

export function ButtonDemo() {
  return (
    <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap' }}>
      {/* Variants */}
      <Button variant="contained">Contained</Button>
      <Button variant="outlined">Outlined</Button>
      <Button variant="text">Text</Button>

      {/* Colors */}
      <Button variant="contained" color="primary">Primary</Button>
      <Button variant="contained" color="secondary">Secondary</Button>
      <Button variant="contained" color="error">Error</Button>
      <Button variant="contained" color="success">Success</Button>

      {/* Sizes */}
      <Button variant="contained" size="small">Small</Button>
      <Button variant="contained" size="medium">Medium</Button>
      <Button variant="contained" size="large">Large</Button>

      {/* With Icons */}
      <Button variant="contained" startIcon={<DeleteIcon />}>
        Delete
      </Button>

      {/* Icon Button */}
      <IconButton color="primary" aria-label="delete">
        <DeleteIcon />
      </IconButton>

      {/* Loading Button */}
      <LoadingButton loading variant="outlined">
        Submit
      </LoadingButton>
      <LoadingButton
        loading
        loadingPosition="start"
        startIcon={<SaveIcon />}
        variant="outlined"
      >
        Save
      </LoadingButton>

      {/* States */}
      <Button variant="contained" disabled>Disabled</Button>
    </div>
  )
}
```

### Form Components

```tsx
import TextField from '@mui/material/TextField'
import Select from '@mui/material/Select'
import MenuItem from '@mui/material/MenuItem'
import FormControl from '@mui/material/FormControl'
import InputLabel from '@mui/material/InputLabel'
import Checkbox from '@mui/material/Checkbox'
import FormControlLabel from '@mui/material/FormControlLabel'
import Radio from '@mui/material/Radio'
import RadioGroup from '@mui/material/RadioGroup'
import Switch from '@mui/material/Switch'
import Slider from '@mui/material/Slider'

export function FormDemo() {
  const [age, setAge] = useState('')

  return (
    <Box component="form" sx={{ display: 'flex', flexDirection: 'column', gap: 2, maxWidth: 400 }}>
      {/* Text Field */}
      <TextField
        label="Email"
        type="email"
        placeholder="you@example.com"
        required
        helperText="We'll never share your email"
      />

      {/* Text Field with Error */}
      <TextField
        error
        label="Password"
        type="password"
        helperText="Password must be at least 8 characters"
      />

      {/* Select Dropdown */}
      <FormControl fullWidth>
        <InputLabel id="age-label">Age</InputLabel>
        <Select
          labelId="age-label"
          value={age}
          label="Age"
          onChange={(e) => setAge(e.target.value)}
        >
          <MenuItem value={10}>Ten</MenuItem>
          <MenuItem value={20}>Twenty</MenuItem>
          <MenuItem value={30}>Thirty</MenuItem>
        </Select>
      </FormControl>

      {/* Checkbox */}
      <FormControlLabel
        control={<Checkbox defaultChecked />}
        label="I agree to the terms and conditions"
      />

      {/* Radio Group */}
      <FormControl>
        <RadioGroup defaultValue="option1">
          <FormControlLabel value="option1" control={<Radio />} label="Option 1" />
          <FormControlLabel value="option2" control={<Radio />} label="Option 2" />
        </RadioGroup>
      </FormControl>

      {/* Switch */}
      <FormControlLabel control={<Switch defaultChecked />} label="Enable notifications" />

      {/* Slider */}
      <Slider
        defaultValue={30}
        valueLabelDisplay="auto"
        step={10}
        marks
        min={0}
        max={100}
      />

      <Button variant="contained" type="submit">Submit</Button>
    </Box>
  )
}
```

### Card Component

```tsx
import Card from '@mui/material/Card'
import CardHeader from '@mui/material/CardHeader'
import CardMedia from '@mui/material/CardMedia'
import CardContent from '@mui/material/CardContent'
import CardActions from '@mui/material/CardActions'
import Avatar from '@mui/material/Avatar'
import IconButton from '@mui/material/IconButton'
import Typography from '@mui/material/Typography'
import FavoriteIcon from '@mui/icons-material/Favorite'
import ShareIcon from '@mui/icons-material/Share'
import MoreVertIcon from '@mui/icons-material/MoreVert'

export function CardDemo() {
  return (
    <Card sx={{ maxWidth: 345 }}>
      <CardHeader
        avatar={
          <Avatar sx={{ bgcolor: 'red' }}>
            R
          </Avatar>
        }
        action={
          <IconButton aria-label="settings">
            <MoreVertIcon />
          </IconButton>
        }
        title="Shrimp and Chorizo Paella"
        subheader="September 14, 2024"
      />
      <CardMedia
        component="img"
        height="194"
        image="/static/images/cards/paella.jpg"
        alt="Paella dish"
      />
      <CardContent>
        <Typography variant="body2" color="text.secondary">
          This impressive paella is a perfect party dish and a fun meal to cook
          together with your guests.
        </Typography>
      </CardContent>
      <CardActions disableSpacing>
        <IconButton aria-label="add to favorites">
          <FavoriteIcon />
        </IconButton>
        <IconButton aria-label="share">
          <ShareIcon />
        </IconButton>
      </CardActions>
    </Card>
  )
}
```

### Dialog (Modal) Component

```tsx
import Dialog from '@mui/material/Dialog'
import DialogActions from '@mui/material/DialogActions'
import DialogContent from '@mui/material/DialogContent'
import DialogContentText from '@mui/material/DialogContentText'
import DialogTitle from '@mui/material/DialogTitle'
import Button from '@mui/material/Button'

export function DialogDemo() {
  const [open, setOpen] = useState(false)

  const handleClickOpen = () => setOpen(true)
  const handleClose = () => setOpen(false)

  return (
    <>
      <Button variant="outlined" onClick={handleClickOpen}>
        Open dialog
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">
          Use Google's location service?
        </DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            Let Google help apps determine location. This means sending anonymous
            location data to Google, even when no apps are running.
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose}>Disagree</Button>
          <Button onClick={handleClose} autoFocus>
            Agree
          </Button>
        </DialogActions>
      </Dialog>
    </>
  )
}
```

---

## The sx Prop (Styling)

MUI's `sx` prop provides a shorthand for styling components:

```tsx
import Box from '@mui/material/Box'

<Box
  sx={{
    width: 300,
    height: 300,
    backgroundColor: 'primary.main',
    '&:hover': {
      backgroundColor: 'primary.dark',
      opacity: [0.9, 0.8, 0.7],
    },
    // Responsive
    fontSize: {
      xs: 12, // 0-600px
      sm: 14, // 600-960px
      md: 16, // 960-1280px
      lg: 18, // 1280-1920px
      xl: 20, // 1920px+
    },
    // Spacing
    p: 2, // padding: theme.spacing(2) = 16px
    m: 1, // margin: theme.spacing(1) = 8px
    mt: 3, // margin-top: 24px
    mx: 'auto', // margin-left and margin-right: auto
  }}
>
  Content
</Box>
```

---

## Layout Components

### Grid System (v2)

```tsx
import Grid from '@mui/material/Grid2'

export function GridDemo() {
  return (
    <Grid container spacing={2}>
      <Grid xs={12} md={8}>
        <Item>xs=12 md=8</Item>
      </Grid>
      <Grid xs={12} md={4}>
        <Item>xs=12 md=4</Item>
      </Grid>
      <Grid xs={6} md={4}>
        <Item>xs=6 md=4</Item>
      </Grid>
      <Grid xs={6} md={4}>
        <Item>xs=6 md=4</Item>
      </Grid>
      <Grid xs={6} md={4}>
        <Item>xs=6 md=4</Item>
      </Grid>
    </Grid>
  )
}
```

### Container & Stack

```tsx
import Container from '@mui/material/Container'
import Stack from '@mui/material/Stack'
import Button from '@mui/material/Button'

export function LayoutDemo() {
  return (
    <Container maxWidth="lg">
      {/* Vertical Stack */}
      <Stack spacing={2}>
        <Button variant="contained">Button 1</Button>
        <Button variant="contained">Button 2</Button>
        <Button variant="contained">Button 3</Button>
      </Stack>

      {/* Horizontal Stack */}
      <Stack direction="row" spacing={2}>
        <Button variant="outlined">Button 1</Button>
        <Button variant="outlined">Button 2</Button>
      </Stack>
    </Container>
  )
}
```

---

## Data Display Components

### Data Grid (MUI X)

```tsx
import { DataGrid, GridColDef } from '@mui/x-data-grid'

const columns: GridColDef[] = [
  { field: 'id', headerName: 'ID', width: 90 },
  { field: 'firstName', headerName: 'First name', width: 150 },
  { field: 'lastName', headerName: 'Last name', width: 150 },
  {
    field: 'age',
    headerName: 'Age',
    type: 'number',
    width: 110,
  },
]

const rows = [
  { id: 1, lastName: 'Snow', firstName: 'Jon', age: 35 },
  { id: 2, lastName: 'Lannister', firstName: 'Cersei', age: 42 },
]

export function DataGridDemo() {
  return (
    <div style={{ height: 400, width: '100%' }}>
      <DataGrid
        rows={rows}
        columns={columns}
        initialState={{
          pagination: {
            paginationModel: { page: 0, pageSize: 5 },
          },
        }}
        pageSizeOptions={[5, 10]}
        checkboxSelection
      />
    </div>
  )
}
```

---

## Form Validation (React Hook Form + MUI)

```tsx
import { useForm, Controller } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import * as z from 'zod'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import Box from '@mui/material/Box'

const schema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
})

type FormData = z.infer<typeof schema>

export function LoginForm() {
  const {
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(schema),
  })

  const onSubmit = (data: FormData) => {
    console.log(data)
  }

  return (
    <Box component="form" onSubmit={handleSubmit(onSubmit)} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
      <Controller
        name="email"
        control={control}
        defaultValue=""
        render={({ field }) => (
          <TextField
            {...field}
            label="Email"
            type="email"
            error={!!errors.email}
            helperText={errors.email?.message}
          />
        )}
      />
      <Controller
        name="password"
        control={control}
        defaultValue=""
        render={({ field }) => (
          <TextField
            {...field}
            label="Password"
            type="password"
            error={!!errors.password}
            helperText={errors.password?.message}
          />
        )}
      />
      <Button type="submit" variant="contained">
        Login
      </Button>
    </Box>
  )
}
```

---

## Best Practices

### 1. Use Theme Spacing
```tsx
// GOOD: Use theme spacing
<Box sx={{ p: 2, m: 1 }} />

// BAD: Hardcode pixels
<Box style={{ padding: '16px', margin: '8px' }} />
```

### 2. Responsive Design
```tsx
// GOOD: Use breakpoints
<Box sx={{ width: { xs: '100%', md: '50%' } }} />

// BAD: Fixed widths
<Box sx={{ width: '600px' }} />
```

### 3. Accessibility
```tsx
// GOOD: Proper ARIA labels
<IconButton aria-label="delete">
  <DeleteIcon />
</IconButton>

// BAD: No label
<IconButton>
  <DeleteIcon />
</IconButton>
```

### 4. Component Composition
```tsx
// GOOD: Compose with MUI components
<Card>
  <CardHeader title="Title" />
  <CardContent>Content</CardContent>
</Card>

// BAD: Build everything from scratch
<div className="card">
  <div className="header">Title</div>
  <div className="content">Content</div>
</div>
```

---

## Resources

- **Official Docs**: https://mui.com/
- **Component API**: https://mui.com/material-ui/api/button/
- **Templates**: https://mui.com/material-ui/getting-started/assets/
- **Icons**: https://mui.com/material-ui/material-icons/
- **GitHub**: https://github.com/mui/material-ui

---

## Related Templates

- `template-ant-design.md` — Enterprise UI library alternative
- `template-chakra-ui.md` — Accessible React component library
- [template-design-system.md](../design-systems/template-design-system.md) — Design system template
