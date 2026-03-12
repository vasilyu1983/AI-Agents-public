# Refactoring Catalog

Comprehensive guide to refactoring patterns based on Martin Fowler's catalog (2nd Edition, 2018) with modern 2026 updates.

## Contents

- [Composing Methods](#composing-methods)
- [Moving Features Between Objects](#moving-features-between-objects)
- [Organizing Data](#organizing-data)
- [Simplifying Conditional Expressions](#simplifying-conditional-expressions)
- [Making Method Calls Simpler](#making-method-calls-simpler)
- [Dealing with Generalization](#dealing-with-generalization)
- [Big Refactorings](#big-refactorings)
- [Modern Refactorings (2026)](#modern-refactorings-2026)
- [References](#references)

---

## Composing Methods

Refactorings that help make methods more readable and maintainable.

### Extract Method

**Problem:** Code fragment that can be grouped together.

**Solution:** Move fragment to separate method with descriptive name.

```javascript
// Before
function printOwing(invoice) {
  printBanner();
  let outstanding = 0;

  for (const order of invoice.orders) {
    outstanding += order.amount;
  }

  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}

// After
function printOwing(invoice) {
  printBanner();
  const outstanding = calculateOutstanding(invoice);
  printDetails(invoice, outstanding);
}

function calculateOutstanding(invoice) {
  return invoice.orders.reduce((sum, order) => sum + order.amount, 0);
}

function printDetails(invoice, outstanding) {
  console.log(`name: ${invoice.customer}`);
  console.log(`amount: ${outstanding}`);
}
```

**When to use:**
- Method is too long (>20 lines)
- Code needs explanation (comment before it)
- Logic can be reused elsewhere

---

### Inline Method

**Problem:** Method body is as clear as its name.

**Solution:** Replace method calls with method body content.

```javascript
// Before
function getRating(driver) {
  return moreThanFiveLateDeliveries(driver) ? 2 : 1;
}

function moreThanFiveLateDeliveries(driver) {
  return driver.lateDeliveries > 5;
}

// After
function getRating(driver) {
  return driver.lateDeliveries > 5 ? 2 : 1;
}
```

**When to use:**
- Method body is self-explanatory
- Over-abstraction adds complexity
- Method is only used once

---

### Extract Variable

**Problem:** Complex expression is hard to understand.

**Solution:** Place result in self-explanatory variable.

```javascript
// Before
if (platform.toUpperCase().includes('MAC') &&
    browser.toUpperCase().includes('IE') &&
    wasInitialized() && resize > 0) {
  // do something
}

// After
const isMacOS = platform.toUpperCase().includes('MAC');
const isIEBrowser = browser.toUpperCase().includes('IE');
const wasResized = wasInitialized() && resize > 0;

if (isMacOS && isIEBrowser && wasResized) {
  // do something
}
```

**When to use:**
- Expression is complex
- Expression is used multiple times
- Variable name adds clarity

---

### Inline Variable

**Problem:** Variable name doesn't add clarity beyond expression itself.

**Solution:** Replace variable references with expression.

```javascript
// Before
const basePrice = order.basePrice;
return basePrice > 1000;

// After
return order.basePrice > 1000;
```

---

### Replace Temp with Query

**Problem:** Temporary variable holds result of expression.

**Solution:** Extract expression into method, use method instead of variable.

```typescript
// Before
class Order {
  quantity: number;
  itemPrice: number;

  getPrice(): number {
    const basePrice = this.quantity * this.itemPrice;
    const discountFactor = 0.98;
    return basePrice * discountFactor;
  }
}

// After
class Order {
  quantity: number;
  itemPrice: number;

  getPrice(): number {
    return this.basePrice() * this.discountFactor();
  }

  private basePrice(): number {
    return this.quantity * this.itemPrice;
  }

  private discountFactor(): number {
    return 0.98;
  }
}
```

---

### Split Temporary Variable

**Problem:** Local variable assigned multiple times (not loop variable or accumulator).

**Solution:** Create separate variable for each assignment.

```javascript
// Before
let temp = 2 * (height + width);
console.log(temp);
temp = height * width;
console.log(temp);

// After
const perimeter = 2 * (height + width);
console.log(perimeter);
const area = height * width;
console.log(area);
```

---

### Remove Assignments to Parameters

**Problem:** Code assigns value to parameter.

**Solution:** Use local variable instead.

```javascript
// Before
function discount(inputValue, quantity) {
  if (inputValue > 50) inputValue -= 2;
  if (quantity > 100) inputValue -= 1;
  return inputValue;
}

// After
function discount(inputValue, quantity) {
  let result = inputValue;
  if (inputValue > 50) result -= 2;
  if (quantity > 100) result -= 1;
  return result;
}
```

---

## Moving Features Between Objects

Refactorings that help move functionality between classes.

### Move Method

**Problem:** Method is used more by another class than by its own.

**Solution:** Move method to the class that uses it most.

```typescript
// Before
class Account {
  overdraftCharge(): number {
    return this.type.isPremium() ? 10 : 20;
  }
}

class AccountType {
  isPremium(): boolean {
    return this.name === 'Premium';
  }
}

// After
class Account {
  overdraftCharge(): number {
    return this.type.overdraftCharge();
  }
}

class AccountType {
  isPremium(): boolean {
    return this.name === 'Premium';
  }

  overdraftCharge(): number {
    return this.isPremium() ? 10 : 20;
  }
}
```

---

### Move Field

**Problem:** Field is used more by another class than by its own.

**Solution:** Move field to class that uses it most.

```typescript
// Before
class Customer {
  plan: Plan;
  discountRate: number;
}

class Plan {
  name: string;
}

// After
class Customer {
  plan: Plan;

  get discountRate(): number {
    return this.plan.discountRate;
  }
}

class Plan {
  name: string;
  discountRate: number;
}
```

---

### Extract Class

**Problem:** Class does work of two or more classes.

**Solution:** Create new class, move relevant fields and methods.

```typescript
// Before
class Person {
  name: string;
  officeAreaCode: string;
  officeNumber: string;

  getTelephoneNumber(): string {
    return `(${this.officeAreaCode}) ${this.officeNumber}`;
  }
}

// After
class Person {
  name: string;
  officeTelephone: TelephoneNumber;

  getTelephoneNumber(): string {
    return this.officeTelephone.toString();
  }
}

class TelephoneNumber {
  areaCode: string;
  number: string;

  toString(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}
```

---

### Inline Class

**Problem:** Class does too little to justify its existence.

**Solution:** Move all features to another class and delete it.

```typescript
// Before
class Person {
  name: string;
  telephone: TelephoneNumber;
}

class TelephoneNumber {
  areaCode: string;
  number: string;

  toString(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}

// After
class Person {
  name: string;
  areaCode: string;
  number: string;

  getTelephoneNumber(): string {
    return `(${this.areaCode}) ${this.number}`;
  }
}
```

---

## Organizing Data

Refactorings that help organize data structures.

### Encapsulate Field

**Problem:** Public field accessed directly.

**Solution:** Make field private, provide accessors.

```typescript
// Before
class Person {
  name: string;
}

const person = new Person();
person.name = 'John';

// After
class Person {
  private _name: string;

  get name(): string {
    return this._name;
  }

  set name(value: string) {
    this._name = value;
  }
}

const person = new Person();
person.name = 'John';
```

---

### Replace Data Value with Object

**Problem:** Data item needs additional data or behavior.

**Solution:** Turn data item into object.

```typescript
// Before
class Order {
  customer: string;
}

// After
class Order {
  customer: Customer;
}

class Customer {
  constructor(private name: string) {}

  getName(): string {
    return this.name;
  }
}
```

---

### Change Value to Reference

**Problem:** Many equal instances of a class should be replaced with single object.

**Solution:** Turn object into reference object.

```typescript
// Before
class Customer {
  constructor(private name: string) {}
}

// Multiple instances created
const customer1 = new Customer('John');
const customer2 = new Customer('John');

// After
class Customer {
  private static instances = new Map<string, Customer>();

  private constructor(private name: string) {}

  static get(name: string): Customer {
    if (!Customer.instances.has(name)) {
      Customer.instances.set(name, new Customer(name));
    }
    return Customer.instances.get(name)!;
  }
}

// Single instance reused
const customer1 = Customer.get('John');
const customer2 = Customer.get('John'); // Same instance
```

---

### Replace Array with Object

**Problem:** Array with elements representing different things.

**Solution:** Replace with object with meaningful field names.

```javascript
// Before
const row = [];
row[0] = 'Liverpool';
row[1] = 15;

// After
const performance = {
  name: 'Liverpool',
  wins: 15
};
```

---

## Simplifying Conditional Expressions

Refactorings that simplify complex conditionals.

### Decompose Conditional

**Problem:** Complex conditional (if-then-else).

**Solution:** Extract methods from condition, then, and else parts.

```javascript
// Before
if (date.before(SUMMER_START) || date.after(SUMMER_END)) {
  charge = quantity * winterRate + winterServiceCharge;
} else {
  charge = quantity * summerRate;
}

// After
if (isSummer(date)) {
  charge = summerCharge(quantity);
} else {
  charge = winterCharge(quantity);
}
```

---

### Consolidate Conditional Expression

**Problem:** Multiple conditionals with same result.

**Solution:** Combine into single conditional expression.

```javascript
// Before
function disabilityAmount(employee) {
  if (employee.seniority < 2) return 0;
  if (employee.monthsDisabled > 12) return 0;
  if (employee.isPartTime) return 0;
  // compute disability amount
}

// After
function disabilityAmount(employee) {
  if (isNotEligibleForDisability(employee)) return 0;
  // compute disability amount
}

function isNotEligibleForDisability(employee) {
  return employee.seniority < 2
    || employee.monthsDisabled > 12
    || employee.isPartTime;
}
```

---

### Replace Nested Conditional with Guard Clauses

**Problem:** Method has conditional behavior that doesn't make normal path clear.

**Solution:** Use guard clauses for special cases.

```javascript
// Before
function getPayAmount() {
  let result;
  if (isDead) {
    result = deadAmount();
  } else {
    if (isSeparated) {
      result = separatedAmount();
    } else {
      if (isRetired) {
        result = retiredAmount();
      } else {
        result = normalPayAmount();
      }
    }
  }
  return result;
}

// After
function getPayAmount() {
  if (isDead) return deadAmount();
  if (isSeparated) return separatedAmount();
  if (isRetired) return retiredAmount();
  return normalPayAmount();
}
```

---

### Replace Conditional with Polymorphism

**Problem:** Conditional based on object type.

**Solution:** Create subclasses matching conditional branches.

```typescript
// Before
class Bird {
  getSpeed(): number {
    switch (this.type) {
      case 'european':
        return this.getBaseSpeed();
      case 'african':
        return this.getBaseSpeed() - this.getLoadFactor();
      case 'norwegian-blue':
        return this.isNailed ? 0 : this.getBaseSpeed();
      default:
        throw new Error('Unknown bird');
    }
  }
}

// After
abstract class Bird {
  abstract getSpeed(): number;
}

class EuropeanBird extends Bird {
  getSpeed(): number {
    return this.getBaseSpeed();
  }
}

class AfricanBird extends Bird {
  getSpeed(): number {
    return this.getBaseSpeed() - this.getLoadFactor();
  }
}

class NorwegianBlueBird extends Bird {
  constructor(private isNailed: boolean) {
    super();
  }

  getSpeed(): number {
    return this.isNailed ? 0 : this.getBaseSpeed();
  }
}
```

---

### Introduce Null Object

**Problem:** Repeated checks for null values.

**Solution:** Replace null value with null object.

```typescript
// Before
class Customer {
  getName(): string {
    return this.name;
  }
}

const customer = getCustomer();
const name = customer === null ? 'occupant' : customer.getName();

// After
class Customer {
  getName(): string {
    return this.name;
  }

  static createNullCustomer(): Customer {
    return new NullCustomer();
  }
}

class NullCustomer extends Customer {
  getName(): string {
    return 'occupant';
  }
}

const customer = getCustomer() || Customer.createNullCustomer();
const name = customer.getName();
```

---

## Making Method Calls Simpler

Refactorings that simplify method interfaces.

### Rename Method

**Problem:** Method name doesn't reveal its purpose.

**Solution:** Rename method.

```javascript
// Before
function getsnm() {
  return this.name;
}

// After
function getSecondName() {
  return this.name;
}
```

---

### Add Parameter

**Problem:** Method needs more information from caller.

**Solution:** Add parameter.

```javascript
// Before
function getContact() {
  return this.name;
}

// After
function getContact(includeTitle) {
  return includeTitle ? `${this.title} ${this.name}` : this.name;
}
```

---

### Remove Parameter

**Problem:** Parameter no longer used by method body.

**Solution:** Remove it.

```javascript
// Before
function getContact(includeTitle) {
  return this.name; // includeTitle never used
}

// After
function getContact() {
  return this.name;
}
```

---

### Separate Query from Modifier

**Problem:** Method returns value and changes object state.

**Solution:** Split into two methods.

```javascript
// Before
function getTotalOutstandingAndSetReadyForSummaries() {
  const total = this.orders.reduce((sum, order) => sum + order.total, 0);
  this.readyForSummaries = true;
  return total;
}

// After
function getTotalOutstanding() {
  return this.orders.reduce((sum, order) => sum + order.total, 0);
}

function setReadyForSummaries() {
  this.readyForSummaries = true;
}
```

---

### Parameterize Method

**Problem:** Multiple methods do similar things with different values.

**Solution:** Create one method using parameter for different values.

```javascript
// Before
function fivePercentRaise() {
  this.salary *= 1.05;
}

function tenPercentRaise() {
  this.salary *= 1.10;
}

// After
function raise(percentage) {
  this.salary *= (1 + percentage / 100);
}
```

---

### Replace Parameter with Explicit Methods

**Problem:** Method runs different code based on parameter values.

**Solution:** Create separate method for each parameter value.

```javascript
// Before
function setValue(name, value) {
  if (name === 'height') this.height = value;
  if (name === 'width') this.width = value;
}

// After
function setHeight(value) {
  this.height = value;
}

function setWidth(value) {
  this.width = value;
}
```

---

### Preserve Whole Object

**Problem:** Getting several values from object and passing as parameters.

**Solution:** Pass whole object instead.

```javascript
// Before
const low = daysTempRange.getLow();
const high = daysTempRange.getHigh();
const withinPlan = plan.withinRange(low, high);

// After
const withinPlan = plan.withinRange(daysTempRange);
```

---

### Replace Parameter with Method Call

**Problem:** Calling method, passing result as parameter to another method.

**Solution:** Make second method call first method directly.

```javascript
// Before
const basePrice = quantity * itemPrice;
const discountLevel = getDiscountLevel();
const finalPrice = discountedPrice(basePrice, discountLevel);

// After
const basePrice = quantity * itemPrice;
const finalPrice = discountedPrice(basePrice);

function discountedPrice(basePrice) {
  const discountLevel = getDiscountLevel();
  // use discountLevel
}
```

---

### Introduce Parameter Object

**Problem:** Methods have long parameter list with natural grouping.

**Solution:** Replace parameters with object.

```typescript
// Before
function amountInvoiced(startDate: Date, endDate: Date) {}
function amountReceived(startDate: Date, endDate: Date) {}
function amountOverdue(startDate: Date, endDate: Date) {}

// After
class DateRange {
  constructor(
    public startDate: Date,
    public endDate: Date
  ) {}
}

function amountInvoiced(dateRange: DateRange) {}
function amountReceived(dateRange: DateRange) {}
function amountOverdue(dateRange: DateRange) {}
```

---

### Remove Setting Method

**Problem:** Field should be set at creation time and never altered.

**Solution:** Remove methods that set field.

```typescript
// Before
class Account {
  private id: string;

  setId(id: string) {
    this.id = id;
  }
}

// After
class Account {
  constructor(private readonly id: string) {}
}
```

---

## Dealing with Generalization

Refactorings that deal with inheritance hierarchies.

### Pull Up Method

**Problem:** Methods with identical results in subclasses.

**Solution:** Move method to superclass.

```typescript
// Before
class Employee {}

class Salesman extends Employee {
  getName(): string {
    return this.name;
  }
}

class Engineer extends Employee {
  getName(): string {
    return this.name;
  }
}

// After
class Employee {
  getName(): string {
    return this.name;
  }
}

class Salesman extends Employee {}
class Engineer extends Employee {}
```

---

### Pull Up Field

**Problem:** Subclasses have same field.

**Solution:** Move field to superclass.

```typescript
// Before
class Employee {}

class Salesman extends Employee {
  name: string;
}

class Engineer extends Employee {
  name: string;
}

// After
class Employee {
  name: string;
}

class Salesman extends Employee {}
class Engineer extends Employee {}
```

---

### Pull Up Constructor Body

**Problem:** Subclasses have constructors with mostly identical bodies.

**Solution:** Create superclass constructor, call from subclass.

```typescript
// Before
class Employee {
  name: string;
  id: string;
}

class Manager extends Employee {
  constructor(name: string, id: string, grade: number) {
    this.name = name;
    this.id = id;
    this.grade = grade;
  }
}

// After
class Employee {
  constructor(name: string, id: string) {
    this.name = name;
    this.id = id;
  }
}

class Manager extends Employee {
  constructor(name: string, id: string, grade: number) {
    super(name, id);
    this.grade = grade;
  }
}
```

---

### Push Down Method

**Problem:** Behavior on superclass relevant only for some subclasses.

**Solution:** Move to those subclasses.

```typescript
// Before
class Employee {
  getQuota(): number {
    return 0; // Only relevant for salesmen
  }
}

class Engineer extends Employee {}
class Salesman extends Employee {}

// After
class Employee {}
class Engineer extends Employee {}

class Salesman extends Employee {
  getQuota(): number {
    return 100;
  }
}
```

---

### Extract Subclass

**Problem:** Class has features used only in some instances.

**Solution:** Create subclass for that subset of features.

```typescript
// Before
class JobItem {
  constructor(
    private unitPrice: number,
    private quantity: number,
    private isLabor: boolean,
    private employee?: Employee
  ) {}

  getTotalPrice(): number {
    return this.unitPrice * this.quantity;
  }

  getUnitPrice(): number {
    return this.isLabor ? this.employee!.getRate() : this.unitPrice;
  }
}

// After
abstract class JobItem {
  constructor(
    protected unitPrice: number,
    protected quantity: number
  ) {}

  getTotalPrice(): number {
    return this.getUnitPrice() * this.quantity;
  }

  abstract getUnitPrice(): number;
}

class PartItem extends JobItem {
  getUnitPrice(): number {
    return this.unitPrice;
  }
}

class LaborItem extends JobItem {
  constructor(
    unitPrice: number,
    quantity: number,
    private employee: Employee
  ) {
    super(unitPrice, quantity);
  }

  getUnitPrice(): number {
    return this.employee.getRate();
  }
}
```

---

### Extract Superclass

**Problem:** Two classes have similar features.

**Solution:** Create superclass, move common features.

```typescript
// Before
class Employee {
  constructor(
    private name: string,
    private id: string
  ) {}

  getName(): string {
    return this.name;
  }
}

class Department {
  constructor(
    private name: string
  ) {}

  getName(): string {
    return this.name;
  }
}

// After
class Party {
  constructor(protected name: string) {}

  getName(): string {
    return this.name;
  }
}

class Employee extends Party {
  constructor(
    name: string,
    private id: string
  ) {
    super(name);
  }
}

class Department extends Party {}
```

---

### Extract Interface

**Problem:** Multiple clients use same subset of class interface.

**Solution:** Move subset to interface.

```typescript
// Before
class Employee {
  getRate(): number {
    return this.rate;
  }

  hasSpecialSkill(): boolean {
    return this.specialSkill !== null;
  }

  getName(): string {
    return this.name;
  }

  getDepartment(): string {
    return this.department;
  }
}

// After
interface Billable {
  getRate(): number;
  hasSpecialSkill(): boolean;
}

class Employee implements Billable {
  getRate(): number {
    return this.rate;
  }

  hasSpecialSkill(): boolean {
    return this.specialSkill !== null;
  }

  getName(): string {
    return this.name;
  }

  getDepartment(): string {
    return this.department;
  }
}
```

---

### Collapse Hierarchy

**Problem:** Superclass and subclass not very different.

**Solution:** Merge them.

```typescript
// Before
class Employee {
  getName(): string {
    return this.name;
  }
}

class Salesman extends Employee {
  getOffice(): string {
    return this.office;
  }
}

// After (if Salesman has minimal difference)
class Employee {
  getName(): string {
    return this.name;
  }

  getOffice(): string {
    return this.office;
  }
}
```

---

## Big Refactorings

Large-scale refactorings for major structural improvements.

### Tease Apart Inheritance

**Problem:** Inheritance hierarchy doing two jobs at once.

**Solution:** Create two hierarchies, use delegation.

---

### Convert Procedural Design to Objects

**Problem:** Code in procedural style.

**Solution:** Turn data records into objects, split behavior into methods.

---

### Separate Domain from Presentation

**Problem:** GUI classes contain domain logic.

**Solution:** Move domain logic to separate domain classes.

---

### Extract Hierarchy

**Problem:** Class doing too much work with many conditional statements.

**Solution:** Create hierarchy of classes, each subclass representing special case.

---

## Modern Refactorings (2026)

### Replace Callback with Promise/Async-Await

**Problem:** Callback hell makes code hard to read.

**Solution:** Use modern async patterns.

```javascript
// Before
function getData(callback) {
  fetchData((error, data) => {
    if (error) {
      callback(error, null);
    } else {
      processData(data, (error, result) => {
        if (error) {
          callback(error, null);
        } else {
          callback(null, result);
        }
      });
    }
  });
}

// After
async function getData() {
  const data = await fetchData();
  const result = await processData(data);
  return result;
}
```

---

### Extract Hook (React-specific)

**Problem:** Component has complex logic mixed with UI.

**Solution:** Extract logic into custom hook.

```javascript
// Before
function UserProfile() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser().then(data => {
      setUser(data);
      setLoading(false);
    });
  }, []);

  return loading ? <Spinner /> : <Profile user={user} />;
}

// After
function useUser() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser().then(data => {
      setUser(data);
      setLoading(false);
    });
  }, []);

  return { user, loading };
}

function UserProfile() {
  const { user, loading } = useUser();
  return loading ? <Spinner /> : <Profile user={user} />;
}
```

---

## References

- **Refactoring: Improving the Design of Existing Code (2nd Edition)** - Martin Fowler
- **Refactoring.guru** - https://refactoring.guru/refactoring
- **Working Effectively with Legacy Code** - Michael Feathers
