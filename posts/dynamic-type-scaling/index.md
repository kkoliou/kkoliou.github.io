---
title: "Dynamic Type Scaling in SwiftUI Components"
date: 2026-04-10
tags: [SwiftUI, Accessibility, Performance]
summary: "Ensure smooth scrolling and consistent layouts in SwiftUI lazy stacks by using Dynamic Type–scaled fixed sizes instead of relying on intrinsic content height."
---

[Apple recommends](https://developer.apple.com/documentation/swiftui/creating-performant-scrollable-stacks) `LazyHStack` and `LazyVStack` so only visible items are laid out. For carousels, this works when each cell has a **stable size**. If height is determined only by content (wrapping text, mixed subviews), **sections disagree**, and you might see different row heights, clipping, or jumps as cells recycle.


## Problem: lazy + intrinsically sized cells

```swift
ScrollView(.horizontal, showsIndicators: false) {
    LazyHStack(alignment: .top, spacing: 12) {
        ForEach(items) { item in
            StoreCard(item: item)
        }
    }
}
```

<div class="post-media-pair">
<video controls>
<source src="dynamic-type-scaling/assets/carousels%20with%20non%20fixed%20height.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>
<img src="dynamic-type-scaling/assets/IMG_0687.PNG" alt="Section with the second card doesn't fit">
</div>

As you can see, each section has a different height, which is determined by the first element of each section. 
Also, there is a section in the screenshot where its height cuts off the second element.


## Solution: scaled fixed frame + dependency on `dynamicTypeSize`

Scale a base constant with `UIFontMetrics`, and read `dynamicTypeSize` so SwiftUI **re-evaluates** when the user changes text size.

```swift
private struct CarouselCell: View {
    let item: Item
    @Environment(\.dynamicTypeSize) private var dynamicTypeSize

    private var rowHeight: CGFloat {
        UIFontMetrics.default.scaledValue(for: 220)
    }

    var body: some View {
        StoreCard(item: item)
            .frame(width: 280, height: rowHeight)
    }
}
```

We have to apply this pattern to images as well.
Instead of using raw `24`, we use `UIFontMetrics.default.scaledValue(for: 24)`. 
This allows them to scale like fonts.

<div class="post-media-pair">
<video controls>
<source src="dynamic-type-scaling/assets/carousels with fixed height.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>
<video controls>
<source src="dynamic-type-scaling/assets/scaling when font size changes.mp4" type="video/mp4">
Your browser does not support the video tag.
</video>
</div>

## LazyVStack performance

`LazyVStack` also wins when rows have a **predictable height**. If every row’s size is inferred by measuring deep, intrinsic content, the system does more layout work to draw the view and figure total height. This can lead to hangs or weird jumps while scrolling.

Giving each row a scaled height replaces the need to measure everything to discover height with a **declared height for the current text setting**. Thus, you remain compatible with the accessibility guidelines and increase the scrolling performance.
