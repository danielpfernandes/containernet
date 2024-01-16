# Containernet

[![Join the chat at https://gitter.im/containernet/Lobby](https://badges.gitter.im/Join%20Chat.svg)](https://gitter.im/containernet/Lobby?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge) [![Build Status](https://travis-ci.org/containernet/containernet.svg?branch=master)](https://travis-ci.org/containernet/containernet)

## Containernet: Mininet fork that allows to use Docker containers as hosts in emulated networks

This fork of Mininet allows to use Docker containers as Mininet hosts. This enables interesting functionalities to built networking/cloud testbeds. The integration is done by subclassing the original Host class.

Based on: **Mininet 2.3.0d6**

* Containernet website: https://containernet.github.io/
* Mininet website:  http://mininet.org
* Original Mininet repository: https://github.com/mininet/mininet

---
## Cite this work

If you use Containernet for your research and/or other publications, please cite (beside the original Mininet paper) the following paper to reference our work:

M. Peuster, H. Karl, and S. v. Rossem: [**MeDICINE: Rapid Prototyping of Production-Ready Network Services in Multi-PoP Environments**](http://ieeexplore.ieee.org/document/7919490/). IEEE Conference on Network Function Virtualization and Software Defined Networks (NFV-SDN), Palo Alto, CA, USA, pp. 148-153. doi: 10.1109/NFV-SDN.2016.7919490. (2016)

Bibtex:

```bibtex
@inproceedings{peuster2016medicine, 
    author={M. Peuster and H. Karl and S. van Rossem}, 
    booktitle={2016 IEEE Conference on Network Function Virtualization and Software Defined Networks (NFV-SDN)}, 
    title={MeDICINE: Rapid prototyping of production-ready network services in multi-PoP environments}, 
    year={2016}, 
    volume={}, 
    number={}, 
    pages={148-153}, 
    doi={10.1109/NFV-SDN.2016.7919490},
    month={Nov}
}
```

---
## NFV multi-PoP Extension

There is an extension of Containernet called [vim-emu](https://osm.etsi.org/wikipub/index.php/VIM_emulator) which is a full-featured multi-PoP emulation platform for NFV scenarios that was developed as part of the [SONATA-NFV](http://www.sonata-nfv.eu) project and is now hosted by the [OpenSource MANO project](https://osm.etsi.org/).

---
## Installation
### Bare-metal installation

* Requires: **Ubuntu Linux 16.04 LTS**
    ```bash
    $ git clone https://github.com/ramonfontes/containernet.git
    $ cd containernet
    $ sudo util/install.sh -W
    ```
    Wait (and have a coffee) ...

### Usage / Run

Start example topology with some empty Docker containers connected to the network.

* `cd containernet`
* run: `sudo python examples/containernet_example.py`
* use: `containernet> d1 ifconfig` to see config of container `d1`

### Topology example

In your custom topology script you can add Docker hosts as follows:

```python
info('*** Adding docker containers\n')
d1 = net.addDocker('d1', ip='10.0.0.251', dimage="ubuntu:trusty")
d2 = net.addDocker('d2', ip='10.0.0.252', dimage="ubuntu:trusty", cpu_period=50000, cpu_quota=25000)
d3 = net.addHost('d3', ip='11.0.0.253', cls=Docker, dimage="ubuntu:trusty", cpu_shares=20)
d4 = net.addDocker('d4', dimage="ubuntu:trusty", volumes=["/:/mnt/vol1:rw"])
```

### Tests

There is a set of Containernet specific unit tests located in `mininet/test/test_containernet.py`. To run these, do:

* `sudo py.test -v mininet/test/test_containernet.py`

---
## Contact

### Support

If you have any questions, please use GitHub's [issue system](https://github.com/containernet/containernet/issues) or Containernet's [Gitter channel](https://gitter.im/containernet/) to get in touch.

### Contribute

Your contributions are very welcome! Please fork the GitHub repository and create a pull request. We use [Travis-CI](https://travis-ci.org/containernet/containernet) to automatically test new commits.

### Lead developer

Manuel Peuster
* Mail: <manuel (dot) peuster (at) upb (dot) de>
* GitHub: [@mpeuster](https://github.com/mpeuster)
* Website: [Paderborn University](https://cs.uni-paderborn.de/cn/person/?tx_upbperson_personsite%5BpersonId%5D=13271&tx_upbperson_personsite%5Bcontroller%5D=Person&cHash=bafec92c0ada0bdfe8af6e2ed99efb4e)
