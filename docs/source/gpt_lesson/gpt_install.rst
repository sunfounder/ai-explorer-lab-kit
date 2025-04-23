OpenAI Initial Configuration
===============================

This chapter provides a step-by-step guide on configuring OpenAI's development environment on a Raspberry Pi. 
You will learn how to register an OpenAI account, obtain the API key, and install the necessary Python dependencies. 
These steps are fundamental for building AI projects like GPT chatbots or speech recognition applications.

**System Requirements**

* Operating System: Raspberry Pi OS or other Debian-based Linux distributions.
* Python Version: 3.7 or higher.
* Active internet connection.


----------------------------------------------

Setting Up a Virtual Environment
------------------------------------------------


To ensure isolated and manageable development, let’s create and activate a virtual environment.

A virtual environment provides an independent Python dependency environment for each project. This is particularly useful for complex projects like GPT, as it avoids conflicts between dependencies and ensures a clean, controlled development space.

#. Use the following command to create a virtual environment named ``my_venv`` with access to system-level packages. The ``--system-site-packages`` option allows the virtual environment to access globally installed packages, such as pre-installed device drivers.

   .. code-block:: shell

      python -m venv --system-site-packages my_venv

#. Navigate to the ``my_venv`` directory and activate the virtual environment:

   .. code-block:: shell

      cd my_venv
      source bin/activate

.. note::

   Always install dependencies and run projects within the virtual environment.


----------------------------------------------

Installing Required Dependencies
-------------------------------------------

Once the virtual environment is activated, proceed with installing the necessary Python and system-level dependencies.


#. Install Python packages within the virtual environment:

   .. code-block:: shell

      pip3 install openai
      pip3 install openai-whisper
      pip3 install SpeechRecognition
      pip3 install -U sox
      pip3 install requests


#. Install system-level dependencies using the ``apt`` package manager with administrative privileges:

   .. code-block:: shell

      sudo apt install python3-pyaudio
      sudo apt install sox

----------------------------------------------

Obtaining an API Key
-----------------------------------------

The OpenAI API provides a simple interface to access advanced AI models for natural language processing, 
image generation, semantic search, and speech recognition.

**Get API Key**

.. note::

   The API key is your unique identifier for accessing OpenAI services. Keep it secure and avoid sharing it publicly.


#. Visit |link_openai_platform| and click the **Create new secret key** button in the top right corner.

   .. image:: img/apt_create_api_key.png
      :width: 700
      :align: center

#. Select the Owner, Name, Project, and permissions as needed, and then click **Create secret key**.

   .. image:: img/apt_create_api_key2.png
      :width: 700
      :align: center

#. Save the generated key in a secure and accessible location. **You will not be able to view it again** through your OpenAI account. If the key is lost, you will need to generate a new one.

   .. image:: img/apt_create_api_key_copy.png
      :width: 700
      :align: center

.. note::
   * Each key has usage limits and request rates. Allocate keys appropriately based on your needs.
   * Avoid hardcoding the key into your scripts; instead, use environment variables for enhanced security.



**Fill in API Key and Assistant ID**

#. Open the ``keys.py`` file with the following command:

   .. code-block:: shell

      nano ~/ai-explorer-lab-kit/gpt_examples/keys.py

#. Add the copied API Key:

   .. code-block:: shell

      OPENAI_API_KEY = "sk-proj-vEBo7Ahxxxx-xxxxx-xxxx"

#. Press ``Ctrl + X``, ``Y``, and then ``Enter`` to save the file and exit.

.. ----------------------------------------------

.. Setting Permissions
.. -----------------------------------------------------

.. Certain examples may require elevated permissions to run successfully within the virtual environment. 
.. Execute the following command to ensure proper permissions:

.. .. code-block:: shell

..    cd ~/ai-explorer-lab-kit/gpt_examples
..    chmod 755 

.. .. warning::
..    Avoid using ``chmod 777`` unless absolutely necessary, as it grants full permissions to all users, which can pose a security risk. Use ``chmod 755`` to grant sufficient permissions while maintaining security.