CREATE TABLE [dbo].[ACS_categories] (
    [Id]            INT           IDENTITY (1, 1) NOT NULL,
    [category]      NVARCHAR (50) NOT NULL,
    [description]   VARCHAR (50)  NULL,
    [endpoint_path] NVARCHAR (50) NULL,
    CONSTRAINT [PK_ACS_categories] PRIMARY KEY CLUSTERED ([Id] ASC)
);

