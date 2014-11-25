# CSS/SASS styleguide

**Table of contents**

* [Sass Conventions](#sass)
* [Naming Conventions](#naming)
    * [u-utilityName](#u-utilityName)
    * [ComponentName](#ComponentName)
    * [ComponentName--modifierName](#ComponentName--modifierName)
    * [ComponentName-descendantName](#ComponentName-descendantName)
    * [ComponentName.is-stateOfComponent](#is-stateOfComponent)

## Sass Conventions
2 spaces for indents.

Prefer reusable classes to IDs.

## Naming Conventions

The following conventions are modified from the SUIT CSS [naming
conventions](https://github.com/suitcss/suit/blob/master/doc/naming-conventions.md)

### [Utilities](utilities.md)

Low-level structural and positional traits. Utilities can be applied directly
to any element within a component.

Syntax: `u-[sm|md|lg-]<utilityName>`

Use utilities in the `_utils` file when applicable.

<a name="u-utilityName"></a>
#### u-utilityName

Utilities must use a camel case name. What follows is an example of how various
utilities can be used to create a simple structure within a component.

```html
<div class="u-cf">
  <a class="u-floatLeft" href="{{url}}">
    <img class="u-block" src="{{src}}" alt="">
  </a>
  <p class="u-sizeFill u-textBreak">
    …
  </p>
</div>
```

#### Responsive utilities

Certain utilities have responsive variants using the patterns: `u-sm-<name>`,
`u-md-<name>`, and `u-lg-<name>` for small, medium, and large Media Query
breakpoints.


### [Components](components.md)

The CSS responsible for component-specific styling.

Syntax: `[<namespace>-]<ComponentName>[--modifierName|-descendentName]`

This has several benefits when reading and writing HTML and CSS:

* It helps to distinguish between the classes for the root of the component,
  descendent elements, and modifications.
* It keeps the specificity of selectors low.
* It helps to decouple presentation semantics from document semantics.

### namespace (optional)

If necessary, components can be prefixed with a namespace. For example, you may
wish to avoid the potential for collisions between libraries and your custom
components by prefixing all your components with a namespace.

```css
.twt-Button { /* … */ }
.twt-Tabs { /* … */ }
```

This makes it clear, when reading the HTML, which components are part of your
library.

<a name="ComponentName"></a>
### ComponentName

The component's name must be written in pascal case. Nothing else in the
HTML/CSS uses pascal case.

```css
.MyComponent { /* … */ }
```

```html
<article class="MyComponent">
  …
</article>
```

<a name="ComponentName--modifierName"></a>
### ComponentName--modifierName

A component modifier is a class that modifies the presentation of the base
component in some form (e.g., for a certain configuration of the component).
Modifier names must be written in camel case and be separated from the
component name by two hyphens. The class should be included in the HTML _in
addition_ to the base component class.

```css
/* Core button */
.Button { /* … */ }
/* Default button style */
.Button--default { /* … */ }
```

```html
<button class="Button Button--default" type="button">…</button>
```

<a name="ComponentName-descendentName"></a>
### ComponentName-descendentName

A component descendent is a class that is attached to a descendent node of a
component. It's responsible for applying presentation directly to the
descendent on behalf of a particular component. Descendent names must be
written in camel case.

```html
<article class="Tweet">
  <header class="Tweet-header">
    <img class="Tweet-avatar" src="{{src}}" alt="{{alt}}">
    …
  </header>
  <div class="Tweet-bodyText">
    …
  </div>
</article>
```

<a name="is-stateOfComponent"></a>
### ComponentName.is-stateOfComponent

Use `is-stateName` to reflect changes to a component's state. The state name
must be camel case. **Never style these classes directly; they should always be
used as an adjoining class.**

This means that the same state names can be used in multiple contexts, but
every component must define its own styles for the state (as they are scoped to
the component).

```css
.Tweet { /* … */ }
.Tweet.is-expanded { /* … */ }
```

```html
<article class="Tweet is-expanded">
  …
</article>
```

### Javascript Selectors

Use `.js-<something>` for selectors used only by Javascript, never style `js-*`
classes directly.

```html
<article class="Tweet is-expanded">
  …
  <button class="btn js-delete">Delete</button>
</article>
```
