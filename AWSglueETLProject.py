import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue.gluetypes import *
from awsglue.dynamicframe import DynamicFrame
from awsglue import DynamicFrame
from pyspark.sql import functions as SqlFuncs


def _find_null_fields(ctx, schema, path, output, nullStringSet, nullIntegerSet, frame):
    if isinstance(schema, StructType):
        for field in schema:
            new_path = path + "." if path != "" else path
            output = _find_null_fields(
                ctx,
                field.dataType,
                new_path + field.name,
                output,
                nullStringSet,
                nullIntegerSet,
                frame,
            )
    elif isinstance(schema, ArrayType):
        if isinstance(schema.elementType, StructType):
            output = _find_null_fields(
                ctx,
                schema.elementType,
                path,
                output,
                nullStringSet,
                nullIntegerSet,
                frame,
            )
    elif isinstance(schema, NullType):
        output.append(path)
    else:
        x, distinct_set = frame.toDF(), set()
        for i in x.select(path).distinct().collect():
            distinct_ = i[path.split(".")[-1]]
            if isinstance(distinct_, list):
                distinct_set |= set(
                    [
                        item.strip() if isinstance(item, str) else item
                        for item in distinct_
                    ]
                )
            elif isinstance(distinct_, str):
                distinct_set.add(distinct_.strip())
            else:
                distinct_set.add(distinct_)
        if isinstance(schema, StringType):
            if distinct_set.issubset(nullStringSet):
                output.append(path)
        elif (
            isinstance(schema, IntegerType)
            or isinstance(schema, LongType)
            or isinstance(schema, DoubleType)
        ):
            if distinct_set.issubset(nullIntegerSet):
                output.append(path)
    return output


def drop_nulls(
    glueContext, frame, nullStringSet, nullIntegerSet, transformation_ctx
) -> DynamicFrame:
    nullColumns = _find_null_fields(
        frame.glue_ctx, frame.schema(), "", [], nullStringSet, nullIntegerSet, frame
    )
    return DropFields.apply(
        frame=frame, paths=nullColumns, transformation_ctx=transformation_ctx
    )


args = getResolvedOptions(sys.argv, ["JOB_NAME"])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args["JOB_NAME"], args)

# Script generated for node S3 bucket
S3bucket_node1 = glueContext.create_dynamic_frame.from_catalog(
    database="gluedb",
    table_name="inputpracticallab",
    transformation_ctx="S3bucket_node1",
)

# Script generated for node Drop Duplicates
DropDuplicates_node1694356891899 = DynamicFrame.fromDF(
    S3bucket_node1.toDF().dropDuplicates(),
    glueContext,
    "DropDuplicates_node1694356891899",
)

# Script generated for node Drop Null Fields
DropNullFields_node1694356930938 = drop_nulls(
    glueContext,
    frame=DropDuplicates_node1694356891899,
    nullStringSet={"", "null"},
    nullIntegerSet={-1},
    transformation_ctx="DropNullFields_node1694356930938",
)

# Script generated for node Select Fields
SelectFields_node1694356999987 = SelectFields.apply(
    frame=DropNullFields_node1694356930938,
    paths=[
        "id",
        "mszoning",
        "lotfrontage",
        "lotarea",
        "street",
        "lotshape",
        "landcontour",
        "utilities",
        "landslope",
        "neighborhood",
        "condition1",
        "condition2",
        "bldgtype",
        "housestyle",
        "overallqual",
        "yearbuilt",
        "roofstyle",
        "yrsold",
        "saletype",
        "salecondition",
    ],
    transformation_ctx="SelectFields_node1694356999987",
)

# Script generated for node Amazon S3
AmazonS3_node1694357126478 = glueContext.write_dynamic_frame.from_options(
    frame=SelectFields_node1694356999987,
    connection_type="s3",
    format="avro",
    connection_options={
        "path": "s3://outputpracticallab",
        "compression": "gzip",
        "partitionKeys": [],
    },
    transformation_ctx="AmazonS3_node1694357126478",
)

job.commit()
