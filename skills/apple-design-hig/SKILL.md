---
name: apple-design-hig
description: Apply Apple Human Interface Guidelines (HIG) for iOS, iPadOS, macOS, watchOS, tvOS, visionOS, and Apple-inspired web/desktop UI. Use when designing, building, auditing, or reviewing user interfaces, SwiftUI/UIKit/AppKit views, typography, color contrast, materials, layouts, navigation, accessibility, or platform-native interactions against Apple's official design standards.
---

# Apple Human Interface Guidelines (HIG)

Design, review, and refine interfaces using Apple's official Human Interface Guidelines (`https://developer.apple.com/design/human-interface-guidelines/`).

## Quick Workflow

1. **Identify Platform & Scope**: Determine the target platform (`iOS`, `iPadOS`, `macOS`, `watchOS`, `tvOS`, `visionOS`, or Apple-styled Web/Desktop) and the relevant HIG pillar (`getting-started`, `foundations`, `patterns`, `components`, `inputs`, `technologies`).
2. **Consult Bundled Catalog or Fetch Live Guidelines**:
   - Read [references/catalog.md](references/catalog.md) for the complete index of 170+ official Apple HIG topics and slugs.
   - Read pillar summaries in `references/` (`foundations.md`, `patterns.md`, `components.md`, `inputs.md`, `technologies.md`, `getting-started.md`).
   - Fetch the latest live guidance for any specific topic slug directly from Apple's DocC JSON API using the bundled script:
     ```bash
     python3 scripts/hig_fetch.py topic <slug>
     # Example: python3 scripts/hig_fetch.py topic color
     # Example: python3 scripts/hig_fetch.py topic buttons
     # Example: python3 scripts/hig_fetch.py topic designing-for-ios
     ```
   - Search across all Apple HIG topics:
     ```bash
     python3 scripts/hig_fetch.py search "<keyword>"
     ```
   - Refresh the bundled reference catalog from Apple's live DocC endpoints:
     ```bash
     python3 scripts/hig_fetch.py sync
     ```
3. **Evaluate & Implement**: Apply the core principles, foundation rules, and component specifications below, enforcing Section 508 / WCAG AA-AAA contrast and accessibility compliance.

## Core Design Principles

- **Hierarchy & Clarity**: Establish a clear visual hierarchy where controls defer to content. Use negative space, grouping, and scale so users immediately understand primary vs. secondary actions.
- **Harmony & Aesthetic Integrity**: Align visual styling, materials, and motion with the app's function and the device's physical form factor.
- **Consistency**: Use system-provided components, SF Symbols, standard navigation idioms, and platform-consistent terminology so interactions feel immediately familiar.
- **Direct Manipulation**: Let users interact directly with on-screen content via gestures, drag-and-drop, or spatial pointers with immediate visual and haptic feedback.
- **Feedback**: Acknowledge every user action clearly and imperceptibly fast through state highlights, subtle spring animations, progress indicators, and haptics.
- **User Control**: Keep the user in charge. Avoid unnecessary modality, label destructive actions clearly, provide undo/redo, and allow easy cancellation.

## Foundations Checklist

- **Accessibility & Contrast**:
  - Maintain at least 4.5:1 contrast ratio for standard text and 3:1 for large text (aim for 7:1 WCAG AAA where possible).
  - Never rely on color alone to communicate status or interactivity; pair color with SF Symbols, labels, or shapes.
  - Support Dynamic Type, VoiceOver labels, Reduced Motion (`prefers-reduced-motion`), Increase Contrast, and Full Keyboard Access.
  - Ensure minimum hit targets of `44x44 pt` on touch platforms (`iOS`/`iPadOS`/`watchOS`), `28x28 pt` on `macOS`, and `60x60 pt` with `12 pt` spacing on `visionOS`.
- **Color & Dark Mode**:
  - Use semantic system colors (`label`, `secondaryLabel`, `systemBackground`, `secondarySystemBackground`, `tintColor`) that adapt automatically between Light, Dark, and Increased Contrast appearances.
  - In Dark Mode, use elevated surface luminance levels rather than drop shadows to convey depth.
- **Typography**:
  - Use **SF Pro** (sans-serif), **SF Compact** (`watchOS`), **SF Mono** (code/tabular numbers), and **New York** (serif).
  - Use built-in text styles (`Large Title`, `Title 1-3`, `Headline`, `Body`, `Callout`, `Subhead`, `Footnote`, `Caption 1-2`) with relative sizing and line heights rather than hardcoded pixel sizes.
- **Layout & Safe Areas**:
  - Respect safe areas, hardware cutouts, home indicators, window controls, and keyboard avoidance regions.
  - Use adaptive layout grids and size classes rather than device-specific dimensions.
- **Materials & Depth**:
  - Use system materials (`ultraThinMaterial`, `thinMaterial`, `regularMaterial`, `thickMaterial`, Liquid Glass) for transient bars, sheets, sidebars, and overlays so background context subtly shines through without sacrificing text legibility.
- **Writing & Copy**:
  - Use action-specific verbs on buttons (`Save Changes`, `Delete Photo` instead of `Yes`/`OK`).
  - Use sentence case for body copy and notifications, and title case or platform-consistent casing for menus, buttons, and navigation titles.

## Platform Quick Reference

- **iOS (`designing-for-ios`)**: Portrait-first ergonomic reachability; bottom tab bars for top-level navigation; pull-down menus and swipe actions; crisp haptic feedback.
- **iPadOS (`designing-for-ipados`)**: Adaptable multi-column split views and collapsible sidebars; pointer hover effects; full keyboard shortcuts; multitasking and drag-and-drop.
- **macOS (`designing-for-macos`)**: Dense, resizable multi-window workflows; menu bar completeness; sidebars + toolbars; precise pointer targets, context menus, and keyboard navigation.
- **watchOS (`designing-for-watchOS`)**: Glanceable single-screen interactions; Digital Crown scrolling; high-contrast dark backgrounds; Complication and Smart Stack integration.
- **tvOS (`designing-for-tvos`)**: 10-foot viewing distance; focus-based directional navigation with parallax/scale focus states; generous spacing and large typography.
- **visionOS (`designing-for-visionos`)**: Glass windows in shared space; indirect eye-gaze + pinch input (highlight on hover); comfortable field-of-view placement; spatial audio and depth cues.

## Keeping Up to Date

This skill is backed by the `apple-design-hig` repository (`https://github.com/mr8lu/apple-design-hig`), which provides both an MCP server (`apple-design-hig-mcp`) and a CLI updater (`uv run apple-design-hig sync`) that pulls directly from Apple's official DocC JSON endpoints.
