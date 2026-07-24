CREATE TABLE [census].[acs_types] (
    [acs_type]    NVARCHAR (10) NOT NULL,
    [description] NVARCHAR (50) NULL,
    CONSTRAINT [PK_acs_types] PRIMARY KEY CLUSTERED ([acs_type] ASC)
);

CREATE TABLE [census].[geography_types] (
    [geo_type_id]       INT             IDENTITY (1, 1) NOT NULL,
    [description]       NVARCHAR (50)   NULL,
    [query_template]    NVARCHAR (100)  NULL,
    [response_key]      NVARCHAR (50)   NULL,
    [acs_type]          NVARCHAR (10)   NOT NULL,
    [year]              INT             NULL,
    [template_flag]     BIT             NULL,   
    CONSTRAINT [PK_geography_types] PRIMARY KEY CLUSTERED ([geo_type_id] ASC),
    CONSTRAINT [FK_geography_types_acs_type] FOREIGN KEY (acs_type) REFERENCES [census].[acs_types] (acs_type)
);


CREATE TABLE [census].[categories] (
    [category]      NVARCHAR (50) NOT NULL,
    [description]   NVARCHAR (50) NULL,
    [endpoint_path] NVARCHAR (50) NULL,
    CONSTRAINT [PK_categories] PRIMARY KEY CLUSTERED ([category] ASC)
);


CREATE TABLE [census].[subcategories] (
    [id]          INT            IDENTITY (1, 1) NOT NULL,
    [category]    NVARCHAR (50)  NOT NULL,
    [subcategory] NVARCHAR (100) NOT NULL,
    [label]       NVARCHAR (100) NULL,
    [description] NVARCHAR (MAX) NULL,
    [raw_text]    NVARCHAR (MAX) NULL,
    [year]        INT            NOT NULL,
    [create_date] DATETIME       NULL,
    CONSTRAINT [PK_subcategories] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_subcategories_categories] FOREIGN KEY ([category]) REFERENCES [census].[categories] ([category]),
    CONSTRAINT [UQ_subcategories_sub_year] UNIQUE ([subcategory], [year])
);


CREATE TABLE [census].[estimates] (
    [id]                 INT            IDENTITY (1, 1) NOT NULL,
    [subcategory]        NVARCHAR (100) NOT NULL,
    [acs_type]           NVARCHAR (10)  NOT NULL,
    [year]               INT            NOT NULL,
    [estimate]           FLOAT (53)     NULL,
    [margin_of_error]    FLOAT (53)     NULL,
    [geo_id]             NVARCHAR (50)  NULL,
    [create_date]        DATETIME       NULL,
    CONSTRAINT [PK_estimates] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_estimates_acs_type] FOREIGN KEY (acs_type) REFERENCES [census].[acs_types] (acs_type),
    CONSTRAINT [FK_estimates_subcategories] FOREIGN KEY (subcategory, year) REFERENCES [census].[subcategories] (subcategory, year)
);


CREATE TABLE [census].[geography] (
    [id]                INT             IDENTITY (1, 1) NOT NULL,
    [geo_id]            NVARCHAR (50)   NULL,
    [geo_type_id]       INT             NULL,
    [description]       NVARCHAR (100)  NULL,
    [year]              INT             NULL,
    [create_date]       DATETIME        NULL,
    CONSTRAINT [PK_geography] PRIMARY KEY CLUSTERED ([id] ASC),
    CONSTRAINT [FK_geography_geography_types] FOREIGN KEY (geo_type_id) REFERENCES [census].[geography_types] (geo_type_id)
);








