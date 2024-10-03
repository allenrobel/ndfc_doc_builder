# Usage

0. The DCNM Ansible Collection must be installed and in your ``PYTHONPATH``

Example

```bash
export PYTHONPATH=$PYTHONPATH:$HOME/repos/ansible_dev/dcnm_fabric/ansible_collections/cisco/dcnm
```

1. Set the following environment variables appropriately for your NDFC installation

```bash
export NDFC_USERNAME=admin
export NDFC_PASSWORD=my_password
export NDFC_IP4=10.1.1.1
export NDFC_DOMAIN=local
```

2. Change directory into the top-level of wherever you cloned this repo

```bash
cd $HOME/repos/ansible_dev/ndfc_doc_builder
```

3. Edit the following script and modify ``template_name`` to the name of the template you want to document.

```bash
vi ./util/build_ndfc_fabric_documentation.py
```

Change:

```python
template_name = "Easy_Fabric"
```

4. Run the script

```bash
./util/build_ndfc_fabric_documentation.py
```

5. The documentation will be printed as YAML.

# Manual fixes required

- type: str should be type: int due to default is int

                    MS_IFC_BGP_AUTH_KEY_TYPE:
                        choices:
                        - 3
                        - 7
                        default: 3
                        description:
                        - 'BGP Key Encryption Type: 3 - 3DES, 7 - Cisco'
                        required: false
                        type: str   (should be int)

                    BGP_AUTH_KEY_TYPE:
                        choices:
                        - 3
                        - 7
                        default: 3
                        description:
                        - 'BGP Key Encryption Type: 3 - 3DES, 7 - Cisco'
                        required: false
                        type: str (should be int)

                    BGW_ROUTING_TAG:
                        default: 54321
                        description:
                        - Routing tag associated with IP address of loopback and DCI interfaces
                        required: false
                        type: str

                    RS_ROUTING_TAG:
                        default: 54321
                        description:
                        - Routing tag associated with Route Server IP for redistribute direct.
                            This is the IP used in eBGP EVPN peering.
                        required: false
                        type: int

                    STP_BRIDGE_PRIORITY:
                        default: 0
                        description:
                        - Bridge priority for the spanning tree in increments of 4096
                        required: false
                        type: str

                    VPC_PEER_LINK_PO:
                        default: 500
                        description:
                        - No description available
                        required: false
                        type: str

                    VPC_PEER_LINK_VLAN:
                        default: 3600
                        description:
                        - 'VLAN range for vPC Peer Link SVI '
                        required: false
                        type: str

- Defines a comma-separated range, which should be str.  default needs to have quotes "0"

                    MST_INSTANCE_RANGE:
                        default: 0
                        description:
                        - 'MST instance range, Example: 0-3,5,7-9, Default is 0'
                        required: false
                        type: str

- IPFM_FABRIC_PARAMETERS

  - default: 1 needs to be default: "1"
                    LINK_STATE_ROUTING_TAG:
                        default: "1"
                        description:
                        - Routing process tag for the fabric
                        required: false
                        type: str

  - List type requires -> elements: str

                    NETFLOW_EXPORTER_LIST:
                        default: ''
                        description:
                        - One or Multiple Netflow Exporters
                        required: false
                        type: list

                    NETFLOW_MONITOR_LIST:
                        default: ''
                        description:
                        - One or Multiple Netflow Monitors
                        required: false
                        type: list


                    NETFLOW_RECORD_LIST:
                        default: ''
                        description:
                        - One or Multiple Netflow Records
                        required: false
                        type: list

                    NETFLOW_SAMPLER_LIST:
                        default: ''
                        description:
                        - One or multiple netflow Samplers. Applicable to N7K only
                        required: false
                        type: list

                    ASM_GROUP_RANGES:
                        default: ''
                        description:
                        - 'ASM group ranges with prefixes (len:4-32) example: 239.1.1.0/25,
                            max 20 ranges. Enabling SPT-Threshold Infinity to prevent switchover
                            to source-tree.'
                        required: false
                        type: list


# Usage for .rst doc generator for DCNM Ansible Collection

https://github.com/ansible-network/collection_prep?tab=readme-ov-file#doc-generator

```bash
cd $HOME/repos
git clone https://github.com/ansible-network/collection_prep.git
cd $HOME/repos/collection_prep
# requires python 3.8
source ${HOME}/py38/bin/activate
pip install . --force
collection_prep_add_docs -p $HOME/repos/ansible_dev/dcnm_fabric/ansible_collections/cisco/dcnm
```

