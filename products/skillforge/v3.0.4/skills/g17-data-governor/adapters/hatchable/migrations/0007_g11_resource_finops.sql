-- REFERENCE_SCOPE Stage30 D4/A11 - provider-neutral G11/G17 Resource FinOps persistence
-- Additive EXPAND_FIRST migration. No destructive DDL.
ALTER TABLE g11_runs ADD COLUMN IF NOT EXISTS provider_account_ref varchar(255);
ALTER TABLE g11_runs ADD COLUMN IF NOT EXISTS provider_workspace_ref varchar(255);
ALTER TABLE g11_runs ADD COLUMN IF NOT EXISTS account_purpose varchar(32);
ALTER TABLE g11_runs ADD COLUMN IF NOT EXISTS surface_ref varchar(64);
ALTER TABLE g11_runs ADD COLUMN IF NOT EXISTS host_ref varchar(128);

ALTER TABLE g11_metrics ADD COLUMN IF NOT EXISTS billing_mode varchar(64);
ALTER TABLE g11_metrics ADD COLUMN IF NOT EXISTS measurement_status varchar(32) NOT NULL DEFAULT 'UNAVAILABLE';
ALTER TABLE g11_metrics ADD COLUMN IF NOT EXISTS measurement_scope varchar(64);
ALTER TABLE g11_metrics ADD COLUMN IF NOT EXISTS source_priority smallint;
ALTER TABLE g11_metrics ADD COLUMN IF NOT EXISTS source_observed_at timestamptz;

CREATE TABLE IF NOT EXISTS g11_resource_observations (
  id bigserial PRIMARY KEY,
  observation_id varchar(128) NOT NULL UNIQUE,
  captured_at timestamptz NOT NULL,
  provider_ref varchar(64) NOT NULL,
  provider_account_ref varchar(255) NOT NULL,
  provider_workspace_ref varchar(255),
  billing_account_ref varchar(255),
  project_ref varchar(128),
  resource_group_ref varchar(255),
  service_ref varchar(128),
  resource_ref varchar(255),
  meter_ref varchar(128) NOT NULL,
  meter_value numeric(24,8),
  meter_limit numeric(24,8),
  meter_remaining numeric(24,8),
  unit varchar(64) NOT NULL,
  reset_at timestamptz,
  period_start timestamptz,
  period_end timestamptz,
  currency varchar(8),
  acquisition_mode varchar(32) NOT NULL,
  persistence_class varchar(32) NOT NULL,
  measurement_status varchar(32) NOT NULL,
  measurement_scope varchar(64) NOT NULL,
  source_ref varchar(255) NOT NULL,
  source_priority smallint NOT NULL,
  source_observed_at timestamptz NOT NULL,
  collector_ref varchar(128) NOT NULL,
  collector_version varchar(64),
  state_hash char(64) NOT NULL,
  schema_version varchar(32) NOT NULL,
  is_test boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_g11_resource_observations__account_time ON g11_resource_observations(provider_account_ref,captured_at DESC);
CREATE INDEX IF NOT EXISTS ix_g11_resource_observations__project_time ON g11_resource_observations(project_ref,captured_at DESC);
CREATE INDEX IF NOT EXISTS ix_g11_resource_observations__meter_time ON g11_resource_observations(meter_ref,captured_at DESC);

CREATE TABLE IF NOT EXISTS g11_billing_ledger (
  id bigserial PRIMARY KEY,
  ledger_id varchar(128) NOT NULL UNIQUE,
  occurred_at timestamptz NOT NULL,
  period_start timestamptz,
  period_end timestamptz,
  provider_ref varchar(64) NOT NULL,
  billing_account_ref varchar(255) NOT NULL,
  provider_account_ref varchar(255),
  provider_workspace_ref varchar(255),
  project_ref varchar(128),
  service_ref varchar(128),
  sku_ref varchar(128),
  meter_ref varchar(128),
  resource_ref varchar(255),
  billing_event_type varchar(64) NOT NULL,
  billing_mode varchar(64) NOT NULL,
  external_reference varchar(255),
  quantity numeric(24,8),
  unit varchar(64),
  amount_original numeric(24,8),
  currency_original varchar(8),
  fx_rate_to_cad numeric(24,10),
  amount_cad numeric(24,8),
  tax_amount_cad numeric(24,8),
  source_ref varchar(255) NOT NULL,
  measurement_status varchar(32) NOT NULL,
  reconciled_at timestamptz,
  schema_version varchar(32) NOT NULL,
  is_test boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS ix_g11_billing_ledger__billing_account_time ON g11_billing_ledger(billing_account_ref,occurred_at DESC);
CREATE INDEX IF NOT EXISTS ix_g11_billing_ledger__provider_account_time ON g11_billing_ledger(provider_account_ref,occurred_at DESC);
CREATE INDEX IF NOT EXISTS ix_g11_billing_ledger__project_time ON g11_billing_ledger(project_ref,occurred_at DESC);