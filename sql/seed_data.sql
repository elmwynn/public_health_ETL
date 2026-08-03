

/* CONFIG SCHEMA */
-- Insert ACS api data
INSERT INTO [config].[api_info]([description], [short_desc], [base_url]) VALUES (N'American Community Survey', N'ACS', N'https://api.census.gov/data/YEAR/acs/TYPE')

-- Insert ACS settings
INSERT INTO [config].[api_settings]([setting_desc], [setting_value]) VALUES (N'ACS_delimiter', N'!!')



/* CENSUS SCHEMA */
-- Insert ACS Type Data 
INSERT INTO [census].[acs_types]([acs_type], [description]) VALUES (N'acs1', N'1-Year Survey')
INSERT INTO [census].[acs_types]([acs_type], [description]) VALUES (N'acs5', N'5-Year Survey')

-- Insert Category Data

INSERT INTO [census].[categories]([category], [description], [endpoint_path]) VALUES (N'DP02', N'Social', N'/profile')
INSERT INTO [census].[categories]([category], [description], [endpoint_path]) VALUES (N'DP03', N'Economic', N'/profile')
INSERT INTO [census].[categories]([category], [description], [endpoint_path]) VALUES (N'DP04', N'Housing', N'/profile')
INSERT INTO [census].[categories]([category], [description], [endpoint_path]) VALUES (N'DP05', N'Demographic', N'/profile')
INSERT INTO [census].[categories]([category], [description]) VALUES (N'B1001', N'Sex By Age')
INSERT INTO [census].[categories]([category], [description], [endpoint_path]) VALUES (N'S1701', N'Poverty', N'/subject')

-- Insert Geography Type Data
INSERT INTO [census].[geography_types]([description], [query_template], [response_key], [acs_type], [template_flag]) VALUES (N'Census Tract', N'?get=NAME&for=tract:*&in=state:39&in=county:153', N'tract', N'acs5', 1)
INSERT INTO [census].[geography_types]([description], [query_template], [response_key], [acs_type], [template_flag]) VALUES (N'Political Subdivision', N'?get=NAME&for=county%20subdivision:*&in=state:39&in=county:153', N'county subdivision', N'acs5', 1)
INSERT INTO [census].[geography_types]([description], [query_template], [response_key], [acs_type]) VALUES (N'County', N'?get=NAME&for=county:153&in=state:39', N'county', N'acs1,acs5')