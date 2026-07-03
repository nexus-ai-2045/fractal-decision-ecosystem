# Fractal Decision Ecosystem Public Kernel

Fractal Decision Ecosystem（FDE）の public kernel は、AI 支援作業を
evidence、scope、publication safety、completion check へ戻すための、
縮小公開版の参照 kernel です。

この public kernel は意図的に小さくしています。private FDE operating
system、full recursive skill layer、source-pointer registry、private
workflows、absorbed dialogues、generator internals、patent-candidate
implementation details は公開しません。

## Public Kernel

FDE は、次の三層で作業を routing します。

1. Core: fact、scope、publication boundary、completion claim を守る。
2. Router: 正しい lane、runtime、public/private path を選ぶ。
3. Leaf: task に必要な最小 source へ pointer する。

この public kernel が公開する general gates は次の 4 つです。

- Pre-execution fact check
- Scope routing
- Publication containment
- Done verification closeout

Scope routing には、作業を main runtime だけで閉じるか bounded delegate へ
分けるかを判定する `Orchestration Probe` を含めます。これは public kernel
の gate 数を増やすものではなく、size、risk、stopline、delegate plan を
最初に分けるための補助 contract です。

## Rights Posture

この public kernel は limited review のための source-available artifact です。
not open source、つまり open source ではありません。Patent license、trademark license、commercial
license、derivative works license、model-training license は付与しません。

詳細は `LICENSE` と `RIGHTS_NOTICE.md` を参照してください。

## Patent Boundary

Patent / filing details は意図的に broad に保ちます。`Patent Pending` /
`特許出願中` は、application が実際に filed されるまで使いません。

Patent claim に関係しうる implementation details は、この public kernel では
意図的に withheld します。
