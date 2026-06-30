# Evaluation And Play

## Why Play Needs A Replay Buffer

FB-MEBE does not train one policy per downstream reward. It trains one
`z`-conditioned actor and a backward map `B`.

At play time, a command reward is converted into a latent:

```text
z_r = E[B(goal) r(goal)]
```

The expectation is approximated using saved replay-buffer observations. That is
why `play.py` needs both:

- `model_step_<step>.pt`
- `replay_buffer_step_<step>.pt`

## Main Play Command

```bash
python scripts/reinforcement_learning/fb_mod/play.py \
    --run-dir "exp_local/fb_mod/Isaac-Flat-Unitree-Go2-Rnd-Full-FB-ABS-v0/Initial Test/2026-06-26_18-40-46" \
    --model-step 150000 \
    --replay-buffer-step 150000
```

## Config Resolution

`scripts/reinforcement_learning/fb_mod/play_config.py:150` resolves:

1. the run directory
2. the model checkpoint
3. the replay-buffer checkpoint
4. the saved training config

If `path: latest`, it searches `exp_*/` and picks the run whose latest model has
the newest modification time. That is convenient locally but risky when many
runs exist.

## Loader

`scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py:9` defines
`FBPolicyLoader`.

It:

1. Finds `hydra_config.yaml` two directories above the model file.
2. Rebuilds actor and backward-map network shapes from the saved config.
3. Loads `actor`, `B`, `policy_normalizer`, and `B_normalizer`.
4. Exposes `act`, `backward_map`, `reward_inference`, and `refresh_z`.

## Evaluation Flow

`scripts/reinforcement_learning/fb_mod/play.py:161` runs one task evaluation:

1. Sample commands with `CMDSampler`.
2. Write `[vx, vy, wz]` into the environment through `eval_task`.
3. Load replay sample into a `DictBuffer`.
4. Sample raw observations and goals.
5. Compute command rewards with `RewardFunction.inference`.
6. Compute `B(goal)` through the loader.
7. Infer `z_r`.
8. Roll out the actor for 250 steps.
9. Record metrics and optional video.

## Command Rewards

Commands are in:

- `scripts/reinforcement_learning/toolbox/config_task.py:10`
- `scripts/reinforcement_learning/toolbox/config_task.py:30`
- `scripts/reinforcement_learning/toolbox/config_task.py:59`

Reward computation is in:

- `scripts/reinforcement_learning/toolbox/functions_reward.py:126`

The reward compares current raw values against command targets:

- linear velocity
- yaw angular velocity
- projected gravity
- base height

## Videos

If `play_cfg.env.video_eval` is true, `play.py` writes video output under:

```text
exp_local/fb_mod/<task>/<timestamp>_play/videos_eval/
```

Default eval video names follow:

```text
<task>_<mode>_250.mp4
```

For the default locomotion list eval:

```text
locomotion_list_250.mp4
```

## Xbox Play

The shell command is:

```bash
./bash/fb_play_xbox.sh
```

It calls:

```bash
python scripts/reinforcement_learning/fb_mod/play_xbox.py "$@"
```

The hardware/control details are not fully documented in checked-in Markdown.
Treat real-robot use as `TODO: verify` unless you inspect the local hardware
setup and Unitree control bridge.
