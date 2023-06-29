include ../../Makefile.mk

build-debian10:
	docker compose up pmmserver1-debian10 -d
	docker compose up primary1-debian10 -d
	docker compose up standby1-debian10 -d
	docker compose up standby2-debian10 -d

build-ubuntu20:
	docker compose up pmmserver1-ubuntu20 -d
	docker compose up primary1-ubuntu20 -d
	docker compose up standby1-ubuntu20 -d
	docker compose up standby2-ubuntu20 -d

build-centos7:
	docker compose up pmmserver1-centos7 -d
	docker compose up primary1-centos7 -d
	docker compose up standby1-centos7 -d
	docker compose up standby2-centos7 -d
