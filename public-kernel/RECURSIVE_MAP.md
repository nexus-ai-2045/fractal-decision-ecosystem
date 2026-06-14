# Recursive Map

Public FDE kernel は、三層の routing map を使います。

```text
User request
  -> Core gate
  -> Router choice
  -> Leaf source pointer
  -> Evidence-backed action or hold
  -> Done verification
```

## Core

Core gates は truth、scope、rights、safety、completion claims を守ります。

## Router

Router logic は、正しい lane、runtime、public/private path を選びます。

## Leaf

Leaf modules は、task に必要な最小 source を指します。private implementation
ではより豊かな source pointers を使いますが、この public kernel では意図的に
非公開にします。
