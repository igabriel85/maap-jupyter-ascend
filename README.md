# Docker container for MAAP Eclipse Che Jupyter workspace

This repository contains the Dockerfile and associated files for building a Docker container for the MAAP Eclipse Che workspace.
It is based on the Universal developer image UBI8 provided by Red Hat.
Workspace is running on Python 3.10.13 and conda environment.


# Building the Docker container
The Docker container used for this workspace can be cloned in this repository:

```bash
git clone https://gitlab.dev.info.uvt.ro/sage/maap/maap-jupyter-ide
```

Please consult the readme for specific details about building this image.

# Eclipse IDE Jupyter

In contrast to the other IDEs, Jupyter is a web-based interactive computing platform. It allows users to 
create and share documents that contain live code, equations, visualizations, and narrative text. Uses include 
data cleaning and transformation, numerical simulation, statistical modeling, data visualization, machine learning, and much more.
In order to use Jupyter as an IDE in Eclipse Che we need to add the Docker image to the plugin registry.

Moreover, in the current version the Jupyter has to run in the same conda environment as the one used by the workspace.
This limitation means that this workspace is only used to bootstrat the IDE startup, all relavant packages are found in the conda environment from the Docker container.

In order to specify what IDE to use, we need to add the following to the `che-theia-ide` plugin in the `che-plugin-registry` repository see
[maap plugin registry](https://gitlab.dev.info.uvt.ro/sage/maap/che-plugin-registry) for details.

## Inline IDE definition

This workspace contains an alternative way of definint an IDE in Eclipse Che. we can specify using the `inline` attribute the
IDE devfile in it's integrity. This is useful when we want to define a workspace with a specific IDE and we don't want to add it to the plugin registry.

```yaml
inline:
  schemaVersion: 2.2.2
  metadata:
      name: jupyter-ide
      displayName: MAAP Jupyter Lab IDE
      description: Jupyter Lab IDE for MAAP
      icon: /images/notebook.svg
      attributes:
        publisher: igabriel85
        version: 1.0.0
        title: Jupyter Lab IDE for MAAP
        repository: 'https://github.com/igabriel85/maap-jupyter-ide'
        firstPublicationDate: '2024-03-12'
  components:
    - name: jupyter-ide
      container:
        image: quay.io/igabriel185/maap-jupyter-ide:latest
        env:
          - name: JUPYTER_NOTEBOOK_DIR
            value: /projects
        mountSources: true
        memoryLimit: 512M
        imagePullPolicy: IfNotPresent
        endpoints:
          - name: jupyter
            targetPort: 8888
            exposure: public
            protocol: https
            attributes:
              type: main
        attributes:
          ports:
            - exposedPort: 8888
```
This yaml file has to be located in the `.che` folder.

## Jupyter IDE as reference

It is also possible to host the IDE devfile in a separate repository and reference it directly:

```yaml
reference: https://<hostname_and_path_to_a_remote_file>/che-editor.yaml

```

