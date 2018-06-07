# Generative Adversarial Imitation Learning (GAIL)

- Original paper: https://arxiv.org/abs/1606.03476

For results benchmarking on MuJoCo, please navigate to [here](result/gail-result.md)

## If you want to train an imitation learning agent

### Step 1: Download expert data

Download the expert data into `./data`, [download link](https://drive.google.com/drive/folders/1h3H4AY_ZBx08hz-Ct0Nxxus-V1melu1U?usp=sharing)

### Step 2: Run GAIL

Run with single thread:

```bash
python -m synthbase.gail.run_mujoco
```

Run with multiple threads:

```bash
mpirun -np 16 python -m synthbase.gail.run_mujoco
```

See help (`-h`) for more options.

#### In case you want to run Behavior Cloning (BC)

```bash
python -m synthbase.gail.behavior_clone
```

See help (`-h`) for more options.


## Contributing

Bug reports and pull requests are welcome on GitHub at https://github.com/synthai/synthbase/pulls.

## Maintainers

- Yuan-Hong Liao, andrewliao11_at_gmail_dot_com
- Ryan Julian, ryanjulian_at_gmail_dot_com

## Others

Thanks to the open source:

- @synthai/imitation
- @carpedm20/deep-rl-tensorflow
