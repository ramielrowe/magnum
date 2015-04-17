.. _dev-quickstart:

=====================
Developer Quick-Start
=====================

This is a quick walkthrough to get you started developing code for Magnum.
This assumes you are already familiar with submitting code reviews to
an OpenStack project.

.. seealso::

   http://docs.openstack.org/infra/manual/developers.html

Setup Dev Environment
=====================

Install prerequisites::

    # Ubuntu/Debian:
    sudo apt-get update
    sudo apt-get install python-dev libssl-dev python-pip libmysqlclient-dev \
                         libxml2-dev libxslt-dev libpq-dev git git-review \
                         libffi-dev gettext python-tox

    # Fedora/RHEL:
    sudo yum install python-devel openssl-devel python-pip mysql-devel \
                     libxml2-devel libxslt-devel postgresql-devel git \
                     git-review libffi-devel gettext

    # openSUSE/SLE 12:
    sudo zypper install git git-review libffi-devel libmysqlclient-devel \
                        libopenssl-devel libxml2-devel libxslt-devel \
                        postgresql-devel python-devel python-flake8 \
                        python-nose python-pip python-setuptools-git \
                        python-testrepository python-tox python-virtualenv \
                        gettext-runtime

    sudo easy_install nose
    sudo pip install virtualenv setuptools-git flake8 tox testrepository

If using RHEL and yum reports "No package python-pip available" and "No
package git-review available", use the EPEL software repository. Instructions
can be found at `<http://fedoraproject.org/wiki/EPEL/FAQ#howtouse>`_.

You may need to explicitly upgrade virtualenv if you've installed the one
from your OS distribution and it is too old (tox will complain). You can
upgrade it individually, if you need to::

    sudo pip install -U virtualenv

Magnum source code should be pulled directly from git::

    # from your home or source directory
    cd ~
    git clone https://git.openstack.org/openstack/magnum
    cd magnum

Set up a local environment for development and testing should be done with tox::

    # create a virtualenv for development
    tox -evenv -- python -V

Activate the virtual environment whenever you want to work in it.
All further commands in this section should be run with the venv active::

    source .tox/venv/bin/activate

All unit tests should be run using tox. To run Magnum's entire test suite::

    # run all tests (unit and pep8)
    tox

To run a specific test, use a positional argument for the unit tests::

    # run a specific test for Python 2.7
    tox -epy27 -- test_conductor

You may pass options to the test programs using positional arguments::

    # run all the Python 2.7 unit tests (in parallel!)
    tox -epy27 -- --parallel

To run only the pep8/flake8 syntax and style checks::

    tox -epep8

When you're done, deactivate the virtualenv::

    deactivate


Exercising the Services Using DevStack
======================================

DevStack does not yet have Magnum support.  It is, however, necessary to
develop Magnum from a devstack environment at the present time.  Magnum depends
on Nova, Heat, and Neutron to create and schedule virtual machines to simulate
bare-metal.  For milestone #2 we intend to introduce support for Ironic
deployment of baremetal nodes.

This session has only been tested on Ubuntu 14.04 (Trusty) and Fedora 20/21.
We recommend users to select one of them if it is possible.

NB: Magnum depends on a command line tool in kubernetes called kubectl
to execute its operations with Kubernetes.  We are addressing this in milestone
#2 by implementing a native ReST client for Kubernetes.  In the meantime, the
required action is to install kubectl manually.

Install binary distribution of kubectl distributed by Google::

    wget https://github.com/GoogleCloudPlatform/kubernetes/releases/download/v0.11.0/kubernetes.tar.gz
    tar -xzvf kubernetes.tar.gz
    sudo cp -a kubernetes/platforms/linux/amd64/kubectl /usr/bin/kubectl

Clone DevStack::

    # Create dir to run devstack from, if not done so already
    sudo mkdir -p /opt/stack
    sudo chown $USER /opt/stack

    git clone https://github.com/openstack-dev/devstack.git /opt/stack/devstack

Copy devstack/localrc with minimal settings required to enable Heat
and Neutron, refer to http://docs.openstack.org/developer/devstack/guides/neutron.html
for more detailed neutron configuration.

To install magnum into devstack, add following settings to local.conf. You need to
make customized setting according to your environment requirement, refer devstack
guide for details.::

     cat > /opt/stack/devstack/local.conf << END
     [[local|localrc]]
     enable_plugin magnum https://github.com/openstack/magnum
     DATABASE_PASSWORD=password
     RABBIT_PASSWORD=password
     SERVICE_TOKEN=password
     SERVICE_PASSWORD=password
     ADMIN_PASSWORD=password
     PUBLIC_INTERFACE=eth1
     END

Run DevStack::

    cd /opt/stack/devstack
    ./stack.sh

At this time, Magnum has only been tested with the Fedora Atomic micro-OS.
Magnum will likely work with other micro-OS platforms, but each one requires
individual support in the heat template.

The fedora-21-atomic-2 image will automatically be added to glance.  You can
still add your own images to use manually through glance.

Create a new shell, and source the devstack openrc script::

    source /opt/stack/devstack/openrc admin admin

    cd ~
    test -f ~/.ssh/id_rsa.pub || ssh-keygen
    nova keypair-add --pub-key ~/.ssh/id_rsa.pub testkey

To get started, list the available commands and resources::

    magnum help

First create a baymodel, which is similar in nature to a flavor.  It informs
Magnum in which way to construct a bay.::

    NIC_ID=$(neutron net-show public | awk '/ id /{print $4}')
    magnum baymodel-create --name testbaymodel --image-id fedora-21-atomic-2 \
                           --keypair-id testkey \
                           --external-network-id $NIC_ID \
                           --dns-nameserver 8.8.8.8 --flavor-id m1.small \
                           --docker-volume-size 5

Next create a bay. Use the baymodel UUID as a template for bay creation.
This bay will result in one master kubernetes node and two minion nodes.::

    magnum bay-create --name testbay --baymodel testbaymodel --node-count 2

The existing bays can be listed as follows::

    magnum bay-list

If you make some code changes and want to test their effects,
just restart either magnum-api or magnum-conductor.  the -e option to
pip install will link to the location from where the source code
was installed.

Magnum reports CREATE_COMPLETE when it is done creating the bay.  Do not create
containers, pods, services, or replication controllers before Magnum finishes
creating the bay. They will likely not be created, causing Magnum to become
confused.

    magnum bay-list

    +--------------------------------------+---------+------------+-----------------+
    | uuid                                 | name    | node_count | status          |
    +--------------------------------------+---------+------------+-----------------+
    | 9dccb1e6-02dc-4e2b-b897-10656c5339ce | testbay | 2          | CREATE_COMPLETE |
    +--------------------------------------+---------+------------+-----------------+

Kubernetes provides a number of examples you can use to check that things
are working. Here's how to set up the replicated redis example. First, create
a pod for the redis-master::

    cd ~/kubernetes/examples/redis
    magnum pod-create --manifest ./redis-master.yaml --bay testbay

Now turn up a service to provide a discoverable endpoint for the redis sentinels
in the cluster::

    magnum service-create --manifest ./redis-sentinel-service.yaml --bay testbay

To make it a replicated redis cluster create replication controllers for the redis
slaves and sentinels::

    sed -i 's/\(replicas: \)1/\1 2/' redis-controller.yaml
    magnum rc-create --manifest ./redis-controller.yaml --bay testbay

    sed -i 's/\(replicas: \)1/\1 2/' redis-sentinel-controller.yaml
    magnum rc-create --manifest ./redis-sentinel-controller.yaml --bay testbay

Full lifecycle and introspection operations for each object are supported.  For
example, magnum bay-create, magnum baymodel-delete, magnum rc-show, magnum service-list.

In this milestone you have to use the kubernetes kubectl tool to explore the
redis cluster in detail::

    export KUBERNETES_MASTER=http://$(nova list | grep kube_master | awk '{print $13}'):8080
    kubectl get pod

The output of `kubectl get pod` indicates the redis-master is running on the
bay host with IP address 10.0.0.5. To access the redis master::

    ssh minion@$(nova list | grep 10.0.0.5 | awk '{print $13}')
    REDIS_ID=$(docker ps | grep redis:v1 | grep k8s_master | awk '{print $1}')
    docker exec -i -t $REDIS_ID redis-cli

    127.0.0.1:6379> set replication:test true
    OK
    ^D

    exit

Now log into one of the other container hosts and access a redis slave from there::

    ssh minion@$(nova list | grep 10.0.0.4 | awk '{print $13}')
    REDIS_ID=$(docker ps | grep redis:v1 | grep k8s_redis | tail -n +2 | awk '{print $1}')
    docker exec -i -t $REDIS_ID redis-cli

    127.0.0.1:6379> get replication:test
    "true"
    ^D

    exit

There are four redis instances, one master and three slaves, running across the bay,
replicating data between one another.

Building a Swarm bay
====================

First, we will need to reconfigure Magnum. We need to set 'cluster_coe' in
the 'k8s_head' section to 'swarm' in the magnum.conf. After changing
magnum.conf restart magnum-api and magnum-conductor.::

    sudo cat >> /etc/magnum/magnum.conf << END_CONFIG
    [k8s_heat]
    cluster_coe=swarm
    END_CONFIG


Next, create a baymodel, it is very similar to the Kubernetes baymodel,
it is only missing some Kubernetes specific arguments.::

    NIC_ID=$(neutron net-show public | awk '/ id /{print $4}')
    magnum baymodel-create --name swarmbaymodel --image-id fedora-21-atomic-2 \
                           --keypair-id testkey \
                           --external-network-id $NIC_ID \
                           --dns-nameserver 8.8.8.8 --flavor-id m1.small

Finally, create the bay. Use the baymodel 'swarmbaymodel' as a template for
bay creation. This bay will result in one swarm manager node and two extra
agent nodes. ::

    magnum bay-create --name swarmbay --baymodel swarmbaymodel --node-count 2


Building developer documentation
================================

If you would like to build the documentation locally, eg. to test your
documentation changes before uploading them for review, run these
commands to build the documentation set::

    # activate your development virtualenv
    source .tox/venv/bin/activate

    # build the docs
    tox -edocs

Now use your browser to open the top-level index.html located at::

    magnum/doc/build/html/index.html
