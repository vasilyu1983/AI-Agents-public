# Code Smells Guide

Comprehensive guide to identifying and fixing code smells based on Martin Fowler's catalog and modern best practices (2026).

## Contents

- [What Are Code Smells?](#what-are-code-smells)
- [Bloaters](#bloaters)
- [Object-Orientation Abusers](#object-orientation-abusers)
- [Change Preventers](#change-preventers)
- [Dispensables](#dispensables)
- [Couplers](#couplers)
- [Modern Code Smells (2026)](#modern-code-smells-2026)
- [Detection Tools](#detection-tools)
- [References](#references)

---

## What Are Code Smells?

**Definition**: Code smells are surface indications that usually correspond to deeper problems in the system. They're not bugs—they don't prevent the program from functioning. Instead, they indicate weaknesses in design that may slow down development or increase the risk of bugs in the future.

**Origin**: The term was popularized by Kent Beck and Martin Fowler in *Refactoring: Improving the Design of Existing Code*.

**Key Principle**: Code smells are subjective and context-dependent. What's a smell in one context might be acceptable in another.

---

## Bloaters

Code, methods, and classes that have increased to enormous proportions.

### Long Method

**Symptoms**:
- Method exceeds 20-30 lines
- Needs comments to explain sections
- Multiple levels of abstraction

**Why it's bad**:
- Hard to understand and maintain
- Difficult to reuse parts
- Higher chance of bugs

**Refactoring**:
- Extract Method
- Replace Temp with Query
- Decompose Conditional

```javascript
// Smell
function processOrder(order) {
  // Validate order (10 lines)
  if (!order.items) throw new Error('No items');
  // ... more validation

  // Calculate total (15 lines)
  let total = 0;
  for (const item of order.items) {
    total += item.price * item.quantity;
  }
  // ... more calculation

  // Apply discounts (20 lines)
  if (order.coupon) {
    // ... discount logic
  }

  // Save to database (10 lines)
  // ... database logic
}

// Fixed
function processOrder(order) {
  validateOrder(order);
  const total = calculateTotal(order);
  const discounted = applyDiscounts(total, order);
  saveOrder(order, discounted);
}
```

---

### Large Class

**Symptoms**:
- Class has 300+ lines
- Class has 10+ methods
- Class has many instance variables
- Class name includes "Manager", "Controller", "Handler" (God Object)

**Why it's bad**:
- Violates Single Responsibility Principle
- Hard to understand and maintain
- Difficult to test

**Refactoring**:
- Extract Class
- Extract Subclass
- Extract Interface

```typescript
// Smell
class UserManager {
  createUser() {}
  deleteUser() {}
  updateUser() {}
  authenticateUser() {}
  authorizeUser() {}
  sendWelcomeEmail() {}
  sendPasswordResetEmail() {}
  generateUserReport() {}
  exportUserData() {}
  importUserData() {}
  validateUserInput() {}
}

// Fixed
class UserService {
  createUser() {}
  deleteUser() {}
  updateUser() {}
}

class AuthenticationService {
  authenticateUser() {}
  authorizeUser() {}
}

class UserEmailService {
  sendWelcomeEmail() {}
  sendPasswordResetEmail() {}
}

class UserReportService {
  generateUserReport() {}
}

class UserDataService {
  exportUserData() {}
  importUserData() {}
}

class UserValidator {
  validateUserInput() {}
}
```

---

### Primitive Obsession

**Symptoms**:
- Using primitives instead of small objects for simple tasks
- Using constants for type codes
- Using string constants for field names

**Why it's bad**:
- Logic scattered across codebase
- No type safety
- Validation repeated everywhere

**Refactoring**:
- Replace Data Value with Object
- Introduce Parameter Object
- Replace Type Code with Class

```typescript
// Smell
function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}

function sendEmail(to: string, subject: string, body: string) {
  if (!validateEmail(to)) {
    throw new Error('Invalid email');
  }
  // send email
}

// Fixed
class Email {
  private constructor(private readonly value: string) {}

  static create(value: string): Email {
    if (!Email.isValid(value)) {
      throw new Error('Invalid email');
    }
    return new Email(value);
  }

  private static isValid(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  toString(): string {
    return this.value;
  }
}

function sendEmail(to: Email, subject: string, body: string) {
  // No validation needed - Email is guaranteed valid
  // send email
}

// Usage
const email = Email.create('user@example.com');
sendEmail(email, 'Hello', 'World');
```

---

### Long Parameter List

**Symptoms**:
- Method has 4+ parameters
- Parameters have natural groupings
- Parameters always passed together

**Why it's bad**:
- Hard to remember parameter order
- Difficult to add new parameters
- Makes method calls verbose

**Refactoring**:
- Introduce Parameter Object
- Preserve Whole Object

```typescript
// Smell
function createUser(
  firstName: string,
  lastName: string,
  email: string,
  phone: string,
  street: string,
  city: string,
  state: string,
  zip: string
) {
  // ...
}

// Fixed
interface UserData {
  name: Name;
  contact: ContactInfo;
  address: Address;
}

interface Name {
  first: string;
  last: string;
}

interface ContactInfo {
  email: string;
  phone: string;
}

interface Address {
  street: string;
  city: string;
  state: string;
  zip: string;
}

function createUser(userData: UserData) {
  // ...
}
```

---

### Data Clumps

**Symptoms**:
- Same group of variables appears in multiple places
- Deleting one variable from group makes others meaningless

**Why it's bad**:
- Repeated data structures
- Missing abstraction
- Changes require updates in multiple places

**Refactoring**:
- Extract Class
- Introduce Parameter Object

```typescript
// Smell
function printInvoice(
  customerName: string,
  customerEmail: string,
  customerPhone: string,
  orderDate: Date,
  orderItems: Item[]
) {}

function sendReceipt(
  customerName: string,
  customerEmail: string,
  customerPhone: string,
  orderDate: Date
) {}

// Fixed
interface Customer {
  name: string;
  email: string;
  phone: string;
}

interface Order {
  customer: Customer;
  date: Date;
  items: Item[];
}

function printInvoice(order: Order) {}
function sendReceipt(order: Order) {}
```

---

## Object-Orientation Abusers

Incomplete or incorrect application of object-oriented principles.

### Switch Statements

**Symptoms**:
- Switch statement based on type code
- Same switch statement in multiple places
- Adding new type requires updating all switches

**Why it's bad**:
- Violates Open-Closed Principle
- Scattered logic
- Easy to forget updating all switches

**Refactoring**:
- Replace Conditional with Polymorphism
- Replace Type Code with State/Strategy

```typescript
// Smell
class Employee {
  type: string;

  getSalary(): number {
    switch (this.type) {
      case 'engineer':
        return 80000;
      case 'manager':
        return 100000;
      case 'salesman':
        return 60000 + this.getCommission();
      default:
        throw new Error('Unknown employee type');
    }
  }

  getBonus(): number {
    switch (this.type) {
      case 'engineer':
        return 5000;
      case 'manager':
        return 10000;
      case 'salesman':
        return this.getCommission() * 0.1;
      default:
        throw new Error('Unknown employee type');
    }
  }
}

// Fixed
abstract class Employee {
  abstract getSalary(): number;
  abstract getBonus(): number;
}

class Engineer extends Employee {
  getSalary(): number {
    return 80000;
  }

  getBonus(): number {
    return 5000;
  }
}

class Manager extends Employee {
  getSalary(): number {
    return 100000;
  }

  getBonus(): number {
    return 10000;
  }
}

class Salesman extends Employee {
  getSalary(): number {
    return 60000 + this.getCommission();
  }

  getBonus(): number {
    return this.getCommission() * 0.1;
  }

  private getCommission(): number {
    // calculate commission
    return 0;
  }
}
```

---

### Temporary Field

**Symptoms**:
- Field set only in certain circumstances
- Field is null or undefined most of the time
- Field used only by specific methods

**Why it's bad**:
- Confusing to understand object state
- Difficult to know when field is valid
- Hidden dependencies

**Refactoring**:
- Extract Class
- Replace Method with Method Object

```typescript
// Smell
class Order {
  items: Item[];
  discount?: number; // Only set during calculation

  calculateTotal(): number {
    const subtotal = this.items.reduce((sum, item) => sum + item.price, 0);
    this.discount = this.calculateDiscount(subtotal);
    return subtotal - this.discount;
  }

  private calculateDiscount(subtotal: number): number {
    // complex discount logic
    return 0;
  }
}

// Fixed
class Order {
  items: Item[];

  calculateTotal(): number {
    const calculator = new OrderCalculator(this.items);
    return calculator.calculateTotal();
  }
}

class OrderCalculator {
  private discount: number;

  constructor(private items: Item[]) {}

  calculateTotal(): number {
    const subtotal = this.calculateSubtotal();
    this.discount = this.calculateDiscount(subtotal);
    return subtotal - this.discount;
  }

  private calculateSubtotal(): number {
    return this.items.reduce((sum, item) => sum + item.price, 0);
  }

  private calculateDiscount(subtotal: number): number {
    // complex discount logic
    return 0;
  }
}
```

---

### Refused Bequest

**Symptoms**:
- Subclass uses only some methods/properties of superclass
- Subclass overrides methods to do nothing or throw errors
- Inheritance used just for code reuse

**Why it's bad**:
- Wrong inheritance hierarchy
- Violates Liskov Substitution Principle
- Misleading design

**Refactoring**:
- Replace Inheritance with Delegation
- Extract Superclass

```typescript
// Smell
class Rectangle {
  constructor(
    protected width: number,
    protected height: number
  ) {}

  setWidth(width: number) {
    this.width = width;
  }

  setHeight(height: number) {
    this.height = height;
  }

  getArea(): number {
    return this.width * this.height;
  }
}

class Square extends Rectangle {
  setWidth(width: number) {
    // Refused bequest - has to override to maintain square
    this.width = width;
    this.height = width;
  }

  setHeight(height: number) {
    // Refused bequest
    this.width = height;
    this.height = height;
  }
}

// Fixed
interface Shape {
  getArea(): number;
}

class Rectangle implements Shape {
  constructor(
    private width: number,
    private height: number
  ) {}

  setWidth(width: number) {
    this.width = width;
  }

  setHeight(height: number) {
    this.height = height;
  }

  getArea(): number {
    return this.width * this.height;
  }
}

class Square implements Shape {
  constructor(private size: number) {}

  setSize(size: number) {
    this.size = size;
  }

  getArea(): number {
    return this.size * this.size;
  }
}
```

---

### Alternative Classes with Different Interfaces

**Symptoms**:
- Two classes do similar things but have different method names
- Interfaces not matching when they should
- Duplicate functionality with different signatures

**Why it's bad**:
- Can't use polymorphism
- Duplicate code
- Harder to maintain

**Refactoring**:
- Rename Method
- Move Method
- Extract Superclass

```typescript
// Smell
class FileReader {
  readFromFile(path: string): string {
    // read file
    return '';
  }
}

class DatabaseReader {
  fetchFromDatabase(id: number): string {
    // read from database
    return '';
  }
}

// Fixed
interface DataReader {
  read(source: string): string;
}

class FileReader implements DataReader {
  read(path: string): string {
    // read file
    return '';
  }
}

class DatabaseReader implements DataReader {
  read(id: string): string {
    // read from database
    return '';
  }
}
```

---

## Change Preventers

Smells that make changes difficult and error-prone.

### Divergent Change

**Symptoms**:
- One class commonly changed in different ways for different reasons
- Class has many reasons to change (violates SRP)

**Why it's bad**:
- Changes affect unrelated functionality
- High chance of introducing bugs
- Difficult to understand impact

**Refactoring**:
- Extract Class
- Extract Superclass

```typescript
// Smell
class User {
  // Authentication concerns
  login() {}
  logout() {}
  changePassword() {}

  // Profile concerns
  updateProfile() {}
  uploadAvatar() {}

  // Notification concerns
  sendEmail() {}
  sendSMS() {}

  // Database concerns
  save() {}
  load() {}
}

// Fixed
class User {
  constructor(
    private auth: AuthenticationService,
    private profile: ProfileService,
    private notifications: NotificationService,
    private repository: UserRepository
  ) {}
}

class AuthenticationService {
  login() {}
  logout() {}
  changePassword() {}
}

class ProfileService {
  updateProfile() {}
  uploadAvatar() {}
}

class NotificationService {
  sendEmail() {}
  sendSMS() {}
}

class UserRepository {
  save() {}
  load() {}
}
```

---

### Shotgun Surgery

**Symptoms**:
- Single change requires many small changes in many classes
- Difficult to find all places that need changes
- Changes scattered across codebase

**Why it's bad**:
- Easy to miss necessary changes
- High chance of bugs
- Time-consuming

**Refactoring**:
- Move Method
- Move Field
- Inline Class

```typescript
// Smell
// Changing how we calculate price requires changes in all these classes
class Order {
  calculatePrice() {
    return this.items.reduce((sum, item) => sum + item.price * 1.1, 0);
  }
}

class Invoice {
  calculateTotal() {
    return this.items.reduce((sum, item) => sum + item.price * 1.1, 0);
  }
}

class ShoppingCart {
  getTotal() {
    return this.items.reduce((sum, item) => sum + item.price * 1.1, 0);
  }
}

// Fixed
class PriceCalculator {
  static calculateItemPrice(item: Item): number {
    return item.price * 1.1;
  }

  static calculateTotalPrice(items: Item[]): number {
    return items.reduce((sum, item) => sum + this.calculateItemPrice(item), 0);
  }
}

class Order {
  calculatePrice() {
    return PriceCalculator.calculateTotalPrice(this.items);
  }
}

class Invoice {
  calculateTotal() {
    return PriceCalculator.calculateTotalPrice(this.items);
  }
}

class ShoppingCart {
  getTotal() {
    return PriceCalculator.calculateTotalPrice(this.items);
  }
}
```

---

### Parallel Inheritance Hierarchies

**Symptoms**:
- Creating subclass requires creating subclass in another hierarchy
- Similar class names in different hierarchies

**Why it's bad**:
- Duplicate structure
- Changes require updates in parallel
- Easy to forget one hierarchy

**Refactoring**:
- Move Method
- Move Field
- Collapse Hierarchy

```typescript
// Smell
abstract class Employee {
  abstract getType(): string;
}

class Engineer extends Employee {
  getType() { return 'Engineer'; }
}

class Manager extends Employee {
  getType() { return 'Manager'; }
}

// Parallel hierarchy
abstract class EmployeeReport {
  abstract generate(): string;
}

class EngineerReport extends EmployeeReport {
  generate() { return 'Engineer report'; }
}

class ManagerReport extends EmployeeReport {
  generate() { return 'Manager report'; }
}

// Fixed
abstract class Employee {
  abstract getType(): string;
  abstract generateReport(): string; // Moved report generation here
}

class Engineer extends Employee {
  getType() { return 'Engineer'; }

  generateReport() {
    return 'Engineer report';
  }
}

class Manager extends Employee {
  getType() { return 'Manager'; }

  generateReport() {
    return 'Manager report';
  }
}
```

---

## Dispensables

Something pointless that should be removed.

### Comments

**Symptoms**:
- Method has long explanatory comment
- Comments explain what code does (not why)
- Commented-out code

**Why it's bad**:
- Code should be self-explanatory
- Comments become outdated
- Dead code clutters codebase

**Refactoring**:
- Extract Method
- Rename Method
- Introduce Assertion

```javascript
// Smell
function calculatePrice(order) {
  // Calculate the base price by multiplying quantity by item price
  let basePrice = order.quantity * order.itemPrice;

  // Apply discount if customer is premium
  // Discount is 10% for premium customers
  if (order.customer.isPremium) {
    basePrice = basePrice * 0.9;
  }

  // Add shipping cost based on weight
  // $5 per pound
  let shippingCost = order.weight * 5;

  return basePrice + shippingCost;
}

// Fixed
function calculatePrice(order) {
  const basePrice = calculateBasePrice(order);
  const discount = calculateDiscount(order, basePrice);
  const shippingCost = calculateShippingCost(order);
  return basePrice - discount + shippingCost;
}

function calculateBasePrice(order) {
  return order.quantity * order.itemPrice;
}

function calculateDiscount(order, basePrice) {
  return order.customer.isPremium ? basePrice * 0.1 : 0;
}

function calculateShippingCost(order) {
  const COST_PER_POUND = 5;
  return order.weight * COST_PER_POUND;
}
```

---

### Duplicate Code

**Symptoms**:
- Same code structure in multiple places
- Similar algorithms with minor differences
- Copy-pasted code blocks

**Why it's bad**:
- Changes must be made in multiple places
- Easy to miss one location
- Increases maintenance cost

**Refactoring**:
- Extract Method
- Pull Up Method
- Form Template Method

```typescript
// Smell
class Report {
  generatePDFReport() {
    // Validate input
    if (!this.data) throw new Error('No data');

    // Format for PDF
    const formatted = this.formatForPDF();

    // Generate report
    return this.generatePDF(formatted);
  }

  generateHTMLReport() {
    // Validate input (duplicate)
    if (!this.data) throw new Error('No data');

    // Format for HTML
    const formatted = this.formatForHTML();

    // Generate report
    return this.generateHTML(formatted);
  }
}

// Fixed
abstract class Report {
  generateReport(): string {
    this.validate();
    const formatted = this.format();
    return this.generate(formatted);
  }

  private validate() {
    if (!this.data) throw new Error('No data');
  }

  protected abstract format(): string;
  protected abstract generate(formatted: string): string;
}

class PDFReport extends Report {
  protected format(): string {
    return this.formatForPDF();
  }

  protected generate(formatted: string): string {
    return this.generatePDF(formatted);
  }
}

class HTMLReport extends Report {
  protected format(): string {
    return this.formatForHTML();
  }

  protected generate(formatted: string): string {
    return this.generateHTML(formatted);
  }
}
```

---

### Lazy Class

**Symptoms**:
- Class does too little to justify its existence
- Class has only a few methods
- Class is just a data holder

**Why it's bad**:
- Unnecessary complexity
- Extra files to maintain
- Cognitive overhead

**Refactoring**:
- Inline Class
- Collapse Hierarchy

```typescript
// Smell
class Address {
  street: string;
  city: string;
}

class Person {
  name: string;
  address: Address; // Just a data holder
}

// Fixed (if Address has no behavior)
class Person {
  name: string;
  street: string;
  city: string;
}
```

---

### Dead Code

**Symptoms**:
- Unused variables, parameters, methods, classes
- Unreachable code (after return)
- Code that's never called

**Why it's bad**:
- Clutters codebase
- Confuses developers
- Maintenance burden

**Refactoring**:
- Delete it!

```javascript
// Smell
function processOrder(order) {
  const oldCalculation = order.total * 1.1; // Never used
  return order.total * 1.05;

  console.log('Processing complete'); // Unreachable
}

function legacyFeature() {
  // Never called anywhere
}

// Fixed
function processOrder(order) {
  return order.total * 1.05;
}
```

---

### Speculative Generality

**Symptoms**:
- Abstract classes with only one subclass
- Unused parameters "for future use"
- Methods that aren't called
- Overcomplicated design "in case we need it"

**Why it's bad**:
- YAGNI (You Aren't Gonna Need It)
- Premature optimization
- Harder to understand

**Refactoring**:
- Collapse Hierarchy
- Inline Class
- Remove Parameter

```typescript
// Smell
abstract class PaymentProcessor {
  abstract process(amount: number, currency?: string, metadata?: any): Promise<void>;
}

class CreditCardProcessor extends PaymentProcessor {
  async process(amount: number, currency?: string, metadata?: any): Promise<void> {
    // Only uses amount, currency and metadata never used
    await this.chargeCreditCard(amount);
  }
}

// Fixed (only one implementation, remove abstraction)
class CreditCardProcessor {
  async process(amount: number): Promise<void> {
    await this.chargeCreditCard(amount);
  }

  private async chargeCreditCard(amount: number): Promise<void> {
    // implementation
  }
}
```

---

## Couplers

Smells that contribute to excessive coupling between classes.

### Feature Envy

**Symptoms**:
- Method uses more features of another class than its own
- Method repeatedly accesses other object's data
- Method seems to belong to another class

**Why it's bad**:
- Logic is in wrong place
- Violates encapsulation
- Hard to maintain

**Refactoring**:
- Move Method
- Extract Method

```typescript
// Smell
class Order {
  items: Item[];

  calculateTotal(): number {
    let total = 0;
    for (const item of this.items) {
      // Accessing product details directly
      total += item.product.getPrice() * item.getQuantity();
      total -= item.product.getDiscount();
    }
    return total;
  }
}

// Fixed
class Order {
  items: Item[];

  calculateTotal(): number {
    return this.items.reduce((sum, item) => sum + item.getTotal(), 0);
  }
}

class Item {
  product: Product;
  quantity: number;

  getTotal(): number {
    return this.product.getDiscountedPrice() * this.quantity;
  }

  getQuantity(): number {
    return this.quantity;
  }
}

class Product {
  price: number;
  discount: number;

  getDiscountedPrice(): number {
    return this.price - this.discount;
  }
}
```

---

### Inappropriate Intimacy

**Symptoms**:
- Classes know too much about each other's internal details
- Classes access each other's private fields
- Bidirectional dependencies

**Why it's bad**:
- Tight coupling
- Changes cascade
- Hard to reuse classes separately

**Refactoring**:
- Move Method/Field
- Extract Class
- Hide Delegate

```typescript
// Smell
class Order {
  customer: Customer;

  getDiscount(): number {
    // Accessing customer's private implementation details
    if (this.customer.loyaltyPoints > 100) {
      return this.total * 0.1;
    }
    return 0;
  }
}

class Customer {
  loyaltyPoints: number; // Exposed to Order
}

// Fixed
class Order {
  customer: Customer;

  getDiscount(): number {
    return this.customer.calculateDiscount(this.total);
  }
}

class Customer {
  private loyaltyPoints: number;

  calculateDiscount(orderTotal: number): number {
    if (this.isLoyalCustomer()) {
      return orderTotal * 0.1;
    }
    return 0;
  }

  private isLoyalCustomer(): boolean {
    return this.loyaltyPoints > 100;
  }
}
```

---

### Message Chains

**Symptoms**:
- Code like `a.getB().getC().getD().doSomething()`
- Long chains of method calls
- Breaking Law of Demeter

**Why it's bad**:
- Client depends on navigation structure
- Changes in chain break client
- Tight coupling

**Refactoring**:
- Hide Delegate
- Extract Method

```typescript
// Smell
class Customer {
  getManager(): Manager {
    return this.account.getDepartment().getManager();
  }
}

const manager = customer.getAccount().getDepartment().getManager();

// Fixed
class Customer {
  getManager(): Manager {
    return this.account.getManager();
  }
}

class Account {
  getManager(): Manager {
    return this.department.getManager();
  }
}

// Client code
const manager = customer.getManager();
```

---

### Middle Man

**Symptoms**:
- Class does nothing but delegate to another class
- Most methods are simple delegations
- Class adds no value

**Why it's bad**:
- Unnecessary indirection
- Extra maintenance
- Confusing design

**Refactoring**:
- Remove Middle Man
- Inline Method

```typescript
// Smell
class Person {
  department: Department;

  getManager(): Manager {
    return this.department.getManager();
  }

  getOffice(): Office {
    return this.department.getOffice();
  }

  getTeam(): Team {
    return this.department.getTeam();
  }
}

// Fixed
class Person {
  department: Department;
}

// Client accesses department directly
const manager = person.department.getManager();
```

---

## Modern Code Smells (2026)

### Callback Hell

**Symptoms**:
- Deeply nested callbacks
- Pyramid of doom
- Hard to read async code

**Refactoring**:
- Replace with Promises
- Use async/await

```javascript
// Smell
function getData(callback) {
  fetchUser((error, user) => {
    if (error) {
      callback(error);
    } else {
      fetchOrders(user.id, (error, orders) => {
        if (error) {
          callback(error);
        } else {
          processOrders(orders, (error, result) => {
            if (error) {
              callback(error);
            } else {
              callback(null, result);
            }
          });
        }
      });
    }
  });
}

// Fixed
async function getData() {
  const user = await fetchUser();
  const orders = await fetchOrders(user.id);
  const result = await processOrders(orders);
  return result;
}
```

---

### Prop Drilling (React)

**Symptoms**:
- Props passed through many components
- Intermediate components don't use props
- Deep component trees with props

**Refactoring**:
- Use Context API
- Use state management (Redux, Zustand)
- Component composition

```javascript
// Smell
function App() {
  const [user, setUser] = useState(null);
  return <Dashboard user={user} />;
}

function Dashboard({ user }) {
  return <Sidebar user={user} />;
}

function Sidebar({ user }) {
  return <UserMenu user={user} />;
}

function UserMenu({ user }) {
  return <div>{user.name}</div>;
}

// Fixed
const UserContext = createContext();

function App() {
  const [user, setUser] = useState(null);
  return (
    <UserContext.Provider value={user}>
      <Dashboard />
    </UserContext.Provider>
  );
}

function Dashboard() {
  return <Sidebar />;
}

function Sidebar() {
  return <UserMenu />;
}

function UserMenu() {
  const user = useContext(UserContext);
  return <div>{user.name}</div>;
}
```

---

### God Object (Anti-pattern)

**Symptoms**:
- Object knows or does too much
- Object has too many dependencies
- Object is hard to test

**Refactoring**:
- Extract Class
- Apply Single Responsibility Principle

---

## Detection Tools

### Static Analysis Tools

- **SonarQube** - Detects code smells, bugs, vulnerabilities
- **ESLint** - JavaScript/TypeScript code quality
- **Pylint** - Python code analysis
- **RuboCop** - Ruby static code analyzer
- **ReSharper** - .NET code quality
- **IntelliJ IDEA** - Built-in inspections

### AI-Powered Detection (2025)

- **GitHub Copilot** - Real-time suggestions
- **Embold** - Anti-pattern detection
- **CodiumAI** - Test-driven refactoring
- **DeepCode** - AI code review

---

## References

- **Refactoring: Improving the Design of Existing Code** - Martin Fowler
- **Code Smells Catalog** - https://luzkan.github.io/smells/
- **Refactoring.guru** - https://refactoring.guru/refactoring/smells
- **Clean Code** - Robert C. Martin
