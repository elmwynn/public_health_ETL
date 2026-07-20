CREATE TABLE [config].[api_info] (
    [api_id]      INT            IDENTITY (1, 1) NOT NULL,
    [description] VARBINARY (50) NULL,
    [short_desc]  VARCHAR (50)   NULL,
    [base_url]    NVARCHAR (MAX) NULL,
    CONSTRAINT [PK_api_info] PRIMARY KEY CLUSTERED ([api_id] ASC)
);

CREATE TABLE [dbo].[api_settings] (
    [Id]            INT           IDENTITY (1, 1) NOT NULL,
    [setting_desc]  NVARCHAR (50) NULL,
    [setting_value] NVARCHAR (50) NULL,
    CONSTRAINT [PK_api_settings] PRIMARY KEY CLUSTERED ([Id] ASC)
);

