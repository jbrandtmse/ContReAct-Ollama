# Epic 2: Web Interface & Analysis Tools

**Expanded Goal**: This epic delivers the user-facing components of the platform, building on the core engine from Epic 1. It provides a user-friendly graphical interface for creating experiment configurations and a rich dashboard for visualizing and analyzing the results from completed runs. Additionally, it includes the standalone script for the specialized PEI assessment.

---

### Story 2.1: Basic Streamlit App and Page Structure
**As a** User, **I want** a basic multi-page web application, **so that** I have a structured interface for the configuration and results dashboards.
**Acceptance Criteria**:
1.  [cite_start]A `dashboard.py` script exists that can be launched with `streamlit run dashboard.py`[cite: 674, 699].
2.  [cite_start]The application starts without errors and displays a sidebar for navigation[cite: 672].
3.  [cite_start]Two pages are present in the navigation: "🧪 Experiment Configuration" and "📊 Results Dashboard"[cite: 676, 677].
4.  Both pages can be navigated to and initially display a placeholder title.

---

### Story 2.2: Implement Experiment Configuration Form
**As a** User, **I want** a form in the web UI to define all parameters for an experiment, **so that** I don't have to write YAML manually.
**Acceptance Criteria**:
1.  [cite_start]The "Experiment Configuration" page displays a form implemented with `st.form`[cite: 681].
2.  [cite_start]The form includes widgets for all required parameters: `run_id`, `model_name`, `cycle_count`, and all `model_options` (e.g., `temperature`, `seed`, etc.)[cite: 681].
3.  Appropriate Streamlit input widgets (e.g., `st.text_input`, `st.number_input`) are used for each parameter.
4.  Form validation ensures `cycle_count` is a positive integer greater than 0
5.  Form validation ensures `run_id` is not empty
6.  Invalid input displays a clear error message using `st.error` or `st.warning`

---

### Story 2.3: Implement Configuration File Saving
**As a** User, **I want** to save the configuration I create in the form to a file, **so that** the experiment runner can use it.
**Acceptance Criteria**:
1.  [cite_start]The form contains a "Save Configuration" submit button[cite: 682].
2.  [cite_start]Upon submission, a new `.yaml` file is created in a `configs/` directory[cite: 682, 701].
3.  The name of the file is based on the `run_id` (e.g., `configs/MyRun-A.yaml`).
4.  The content of the generated file is valid YAML and accurately reflects all values entered in the form.
5.  If file save fails (e.g., permissions error, disk full), a clear error message is displayed to the user
6.  On successful save, a success message confirms the file was saved with its path

---

### Story 2.4: Implement Configuration File Loading and Editing
**As a** User, **I want** to load and edit my existing configurations in the web UI, **so that** I can easily modify or review past experiment setups.
**Acceptance Criteria**:
1.  [cite_start]The "Experiment Configuration" page features a dropdown menu that lists all existing `.yaml` files in the `configs/` directory[cite: 683].
2.  [cite_start]Selecting a file from the dropdown automatically populates the form fields with the values from that file[cite: 684].
3.  [cite_start]Submitting the form after loading an existing configuration overwrites the original file with the updated values[cite: 684].

---

### Story 2.5: Implement Results Dashboard Run Selector and Data Loading
**As a** User, **I want** to select a completed experiment run in the results dashboard, **so that** I can view its data.
**Acceptance Criteria**:
1.  [cite_start]The "Results Dashboard" page features a dropdown menu that lists available runs by scanning the `logs/` directory for `.jsonl` files[cite: 688, 689].
2.  [cite_start]Selecting a run from the dropdown triggers the application to read the corresponding `.jsonl` file[cite: 690].
3.  [cite_start]The data from the selected log file is successfully parsed and loaded into a Pandas DataFrame without errors[cite: 690].
4.  If no `.jsonl` files exist in the `logs/` directory, a helpful message instructs the user to run an experiment first
5.  If a log file is corrupted or contains invalid JSON, an error message is displayed and the application doesn't crash
6.  A loading indicator (e.g., `st.spinner`) is shown while the log file is being read and parsed

---

### Story 2.6: Display Summary Metrics on Dashboard
**As a** User, **I want** to see the key summary metrics of a selected run at a glance, **so that** I can quickly understand the high-level results.
**Acceptance Criteria**:
1.  [cite_start]After a run is selected, the dashboard displays key summary metrics (e.g., total memory operations, messages to operator) using `st.metric` widgets[cite: 691].
2.  [cite_start]A complete table of all summary metrics for the run is displayed using `st.dataframe`[cite: 691].
3.  [cite_start]If a PEI assessment log exists for the run, its results are also displayed in a table[cite: 692].

---

### Story 2.7: Display Raw Conversation Log on Dashboard
**As a** User, **I want** to be able to view the detailed conversation history of a run, **so that** I can perform a deep analysis of the agent's reasoning.
**Acceptance Criteria**:
1.  [cite_start]The dashboard includes an expandable section implemented with `st.expander`[cite: 696].
2.  When expanded, this section displays the raw conversation history (e.g., thoughts, tool calls, reflections) from the loaded log file.
3.  The display is formatted for readability.

---

### Story 2.8: Implement Interactive Charts on Dashboard
**As a** User, **I want** to see interactive charts of the experimental data, **so that** I can visually explore and compare results.
**Acceptance Criteria**:
1.  [cite_start]The dashboard displays at least one interactive chart created with Plotly (e.g., a bar chart showing tool calls per cycle)[cite: 693].
2.  [cite_start]The chart is rendered using `st.plotly_chart` and is interactive (e.g., allows hovering to see data points)[cite: 670].
3.  The chart accurately visualizes data from the selected run's DataFrame.
4.  If chart rendering fails or data is insufficient, a clear error or informational message is displayed instead of crashing

---

### Story 2.9: Implement PEI Assessment Script
**As a** Researcher, **I want** a standalone script to perform the PEI assessment on a completed run, **so that** I can replicate the cross-model evaluation from the paper.
**Acceptance Criteria**:
1.  [cite_start]A `run_pei_assessment.py` script exists that accepts command-line arguments for a run log path, an evaluator model, and an output path[cite: 648].
2.  [cite_start]The script correctly reconstructs the 10-cycle message history from the specified `.jsonl` file[cite: 651, 652].
3.  [cite_start]The script successfully invokes the specified evaluator model with the reconstructed history and the verbatim PEI scale prompt[cite: 655, 277].
4.  [cite_start]The script writes the evaluator model's rating to the specified output log file in a structured JSON format[cite: 657, 658].
