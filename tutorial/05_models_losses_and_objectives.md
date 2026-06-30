# Models, Losses, And Objectives

## Network Objects

The original model is `scripts/reinforcement_learning/fb_mod/agent_meta/fb/model.py:38`.

It creates:

- `_forward_map`: `F(obs, z, action) -> z_dim`
- `_backward_map`: `B(goal) -> z_dim`
- `_actor`: `pi(policy_obs, z) -> action distribution`
- optional `_critic`: `Q_reg(critic_obs, action) -> scalar`
- target copies for F, B, and optional critic
- batch-normalization normalizers for policy, F, B, and critic inputs

Network builders live in
`scripts/reinforcement_learning/fb_mod/agent_meta/nn_models.py`.

## Latent `z`

`FBModel.sample_z` at `model.py:88` samples Gaussian vectors and projects them
to the sphere if `model.archi.norm_z` is true.

Projection is:

```text
z = sqrt(z_dim) * normalize(z)
```

This matches the paper's representation space: the unit hypersphere scaled by
`sqrt(d)`.

## Forward/Backward Update

`FBAgent.update_fb` starts at
`scripts/reinforcement_learning/fb_mod/agent_meta/fb/agent.py:254`.

The update computes:

```text
Fs = F(obs, z, action)
B = B(next_goal)
Ms = Fs @ B.T
target_Ms = target_F(next_obs, z, next_action) @ target_B(next_goal).T
```

The loss has:

- an off-diagonal squared TD error term
- a diagonal attraction term
- an orthonormality loss on B
- optional Q regularization for `F(s,a,z)^T z`

The diagonal/off-diagonal structure implements the contrastive FB objective:
positive pairs are actual next goals, while other sampled goals are negatives.

## Actor Update

`FBAgent.update_td3_actor` starts at `agent.py:362`.

The actor samples an action and computes:

```text
Q_fb = (F(obs, z, action) * z).sum(-1)
actor_loss = -Q_fb.mean()
```

If the regularization critic is enabled:

```text
actor_loss -= reg_coeff * Q_reg(obs_critic, action).mean()
```

The Go2 config enables the critic:

```yaml
agent:
  model:
    archi:
      critic:
        enable: true
```

## Regularization Critic

`FBAgent.update_critic` starts at `agent.py:391`.

It is a standard TD critic over `reward_reg`:

```text
target_Q = reward_reg + discount * target_Q_reg(next_obs, next_action)
critic_loss = mse(Q_reg(obs, action), target_Q)
```

This corresponds to the paper's behavior regularizer objective in
`Supplementary_Materials.tex`, Regularized Exploration.

## MEBE Density Sampler

The paper's practical FB-MEBE samples exploration behaviors from replay-buffer
states inversely proportional to estimated density.

In the repo:

- `NF_AGENT` is in
  `scripts/reinforcement_learning/fb_mod/density_estimator/agent_normalizing_flow.py:24`.
- The RealNVP-style flow is in
  `scripts/reinforcement_learning/fb_mod/density_estimator/model_normalizing_flow.py:96`.
- `FBAgent.sample_mixed_z` at `agent.py:140` mixes inverse-density goals with
  random sphere samples.
- `FBAgent.refresh_z` at `agent.py:467` refreshes per-env exploration latents
  during data collection.

Current default:

```yaml
agent:
  train:
    train_goal_ratio: 0.8
```

For training batches, `sample_mixed_z` uses `train_goal_ratio` directly: with the
Go2 default, 80 percent of the batch comes from inverse-density goals and 20
percent from random sphere samples.

Rollout-time latent refresh is separate. `refresh_z` waits until the density
buffer has more than `num_envs * 10` samples, then uses its own hard-coded
`p_reverse = 0.8`; before that gate, it samples random sphere latents.

## Reward Inference

The important test-time operation is:

```text
z_r = E[B(goal) * reward(goal)]
```

Original training-time implementation:

- `scripts/reinforcement_learning/fb_mod/agent_meta/fb/model.py:133`

Play-time loader implementation:

- `scripts/reinforcement_learning/fb_mod/loader/fb_net_loader.py::FBPolicyLoader.reward_inference`

The reward values come from:

- `scripts/reinforcement_learning/toolbox/functions_reward.py:126`

The sampled goals and raw observations come from the saved replay-buffer sample:

```text
models/replay_buffer_step_<step>.pt
```

## Checkpoint Contract

`FBAgent.save` at `agent.py:488` writes:

```text
actor
policy_normalizer
B
B_normalizer
```

It does not save F or the critic because play only needs:

- actor: run the policy
- B: infer reward embedding
- normalizers: match training-time input normalization

This is why a replay-buffer sample is saved beside the model checkpoint.
