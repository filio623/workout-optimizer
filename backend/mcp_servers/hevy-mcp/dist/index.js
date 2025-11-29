#!/usr/bin/env node
// Generated with tsup
// https://github.com/egoist/tsup

// src/index.ts
import { fileURLToPath } from "url";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z as z42 } from "zod";

// package.json
var name = "hevy-mcp";
var version = "1.12.5";

// src/tools/folders.ts
import { z } from "zod";

// src/utils/error-handler.ts
function createErrorResponse(error, context) {
  const errorMessage = error instanceof Error ? error.message : String(error);
  const errorCode = error instanceof Error && "code" in error ? error.code : void 0;
  const errorType = determineErrorType(error, errorMessage);
  if (errorCode) {
    console.debug(`Error code: ${errorCode}`);
  }
  const contextPrefix = context ? `[${context}] ` : "";
  const formattedMessage = `${contextPrefix}Error: ${errorMessage}`;
  console.error(`${formattedMessage} (Type: ${errorType})`, error);
  return {
    content: [
      {
        type: "text",
        text: formattedMessage
      }
    ],
    isError: true
  };
}
function determineErrorType(error, message) {
  const messageLower = message.toLowerCase();
  const nameLower = error instanceof Error ? error.name.toLowerCase() : "";
  if (nameLower.includes("network") || messageLower.includes("network") || nameLower.includes("fetch") || messageLower.includes("fetch") || nameLower.includes("timeout") || messageLower.includes("timeout")) {
    return "NETWORK_ERROR" /* NETWORK_ERROR */;
  }
  if (nameLower.includes("validation") || messageLower.includes("validation") || messageLower.includes("invalid") || messageLower.includes("required")) {
    return "VALIDATION_ERROR" /* VALIDATION_ERROR */;
  }
  if (messageLower.includes("not found") || messageLower.includes("404") || messageLower.includes("does not exist")) {
    return "NOT_FOUND" /* NOT_FOUND */;
  }
  if (nameLower.includes("api") || messageLower.includes("api") || messageLower.includes("server error") || messageLower.includes("500")) {
    return "API_ERROR" /* API_ERROR */;
  }
  return "UNKNOWN_ERROR" /* UNKNOWN_ERROR */;
}
function withErrorHandling(fn, context) {
  return (async (...args) => {
    try {
      return await fn(...args);
    } catch (error) {
      return createErrorResponse(error, context);
    }
  });
}

// src/utils/formatters.ts
function formatWorkout(workout) {
  return {
    id: workout.id,
    title: workout.title,
    description: workout.description,
    startTime: workout.start_time,
    endTime: workout.end_time,
    createdAt: workout.created_at,
    updatedAt: workout.updated_at,
    duration: calculateDuration(workout.start_time, workout.end_time),
    exercises: workout.exercises?.map((exercise) => {
      return {
        index: exercise.index,
        name: exercise.title,
        exerciseTemplateId: exercise.exercise_template_id,
        notes: exercise.notes,
        supersetsId: exercise.supersets_id,
        sets: exercise.sets?.map((set) => ({
          index: set.index,
          type: set.type,
          weight: set.weight_kg,
          reps: set.reps,
          distance: set.distance_meters,
          duration: set.duration_seconds,
          rpe: set.rpe,
          customMetric: set.custom_metric
        }))
      };
    })
  };
}
function formatRoutine(routine) {
  return {
    id: routine.id,
    title: routine.title,
    folderId: routine.folder_id,
    createdAt: routine.created_at,
    updatedAt: routine.updated_at,
    exercises: routine.exercises?.map((exercise) => {
      return {
        name: exercise.title,
        index: exercise.index,
        exerciseTemplateId: exercise.exercise_template_id,
        notes: exercise.notes,
        supersetId: exercise.supersets_id,
        restSeconds: exercise.rest_seconds,
        sets: exercise.sets?.map((set) => ({
          index: set.index,
          type: set.type,
          weight: set.weight_kg,
          reps: set.reps,
          ...set.rep_range !== void 0 && { repRange: set.rep_range },
          distance: set.distance_meters,
          duration: set.duration_seconds,
          ...set.rpe !== void 0 && { rpe: set.rpe },
          customMetric: set.custom_metric
        }))
      };
    })
  };
}
function formatRoutineFolder(folder) {
  return {
    id: folder.id,
    title: folder.title,
    createdAt: folder.created_at,
    updatedAt: folder.updated_at
  };
}
function calculateDuration(startTime, endTime) {
  if (!startTime || !endTime) return "Unknown duration";
  try {
    const start = new Date(startTime);
    const end = new Date(endTime);
    if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) {
      return "Unknown duration";
    }
    const durationMs = end.getTime() - start.getTime();
    if (durationMs < 0) {
      return "Invalid duration (end time before start time)";
    }
    const hours = Math.floor(durationMs / (1e3 * 60 * 60));
    const minutes = Math.floor(durationMs % (1e3 * 60 * 60) / (1e3 * 60));
    const seconds = Math.floor(durationMs % (1e3 * 60) / 1e3);
    return `${hours}h ${minutes}m ${seconds}s`;
  } catch (error) {
    console.error("Error calculating duration:", error);
    return "Unknown duration";
  }
}
function formatExerciseTemplate(template) {
  return {
    id: template.id,
    title: template.title,
    type: template.type,
    primaryMuscleGroup: template.primary_muscle_group,
    secondaryMuscleGroups: template.secondary_muscle_groups,
    isCustom: template.is_custom
  };
}

// src/utils/response-formatter.ts
function createJsonResponse(data, options = { pretty: true, indent: 2 }) {
  const jsonString = options.pretty ? JSON.stringify(data, null, options.indent) : JSON.stringify(data);
  return {
    content: [
      {
        type: "text",
        text: jsonString
      }
    ]
  };
}
function createEmptyResponse(message = "No data found") {
  return {
    content: [
      {
        type: "text",
        text: message
      }
    ]
  };
}

// src/tools/folders.ts
function registerFolderTools(server, hevyClient) {
  server.tool(
    "get-routine-folders",
    "Get a paginated list of your routine folders, including both default and custom folders. Useful for organizing and browsing your workout routines.",
    {
      page: z.coerce.number().int().gte(1).default(1),
      pageSize: z.coerce.number().int().gte(1).lte(10).default(5)
    },
    withErrorHandling(
      async ({ page, pageSize }) => {
        if (!hevyClient) {
          throw new Error(
            "API client not initialized. Please provide HEVY_API_KEY."
          );
        }
        const data = await hevyClient.getRoutineFolders({
          page,
          pageSize
        });
        const folders = data?.routine_folders?.map(
          (folder) => formatRoutineFolder(folder)
        ) || [];
        if (folders.length === 0) {
          return createEmptyResponse(
            "No routine folders found for the specified parameters"
          );
        }
        return createJsonResponse(folders);
      },
      "get-routine-folders"
    )
  );
  server.tool(
    "get-routine-folder",
    "Get complete details of a specific routine folder by its ID, including name, creation date, and associated routines.",
    {
      folderId: z.string().min(1)
    },
    withErrorHandling(async ({ folderId }) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.getRoutineFolder(folderId);
      if (!data) {
        return createEmptyResponse(
          `Routine folder with ID ${folderId} not found`
        );
      }
      const folder = formatRoutineFolder(data);
      return createJsonResponse(folder);
    }, "get-routine-folder")
  );
  server.tool(
    "create-routine-folder",
    "Create a new routine folder in your Hevy account. Requires a name for the folder. Returns the full folder details including the new folder ID.",
    {
      name: z.string().min(1)
    },
    withErrorHandling(async ({ name: name2 }) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.createRoutineFolder({
        routine_folder: {
          title: name2
        }
      });
      if (!data) {
        return createEmptyResponse(
          "Failed to create routine folder: Server returned no data"
        );
      }
      const folder = formatRoutineFolder(data);
      return createJsonResponse(folder, {
        pretty: true,
        indent: 2
      });
    }, "create-routine-folder")
  );
}

// src/tools/routines.ts
import { z as z2 } from "zod";
function registerRoutineTools(server, hevyClient) {
  server.tool(
    "get-routines",
    "Get a paginated list of your workout routines, including custom and default routines. Useful for browsing or searching your available routines.",
    {
      page: z2.coerce.number().int().gte(1).default(1),
      pageSize: z2.coerce.number().int().gte(1).lte(10).default(5)
    },
    withErrorHandling(async (args) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const { page, pageSize } = args;
      const data = await hevyClient.getRoutines({
        page,
        pageSize
      });
      const routines = data?.routines?.map((routine) => formatRoutine(routine)) || [];
      if (routines.length === 0) {
        return createEmptyResponse(
          "No routines found for the specified parameters"
        );
      }
      return createJsonResponse(routines);
    }, "get-routines")
  );
  server.tool(
    "get-routine",
    "Get a routine by its ID using the direct endpoint. Returns all details for the specified routine.",
    {
      routineId: z2.string().min(1)
    },
    withErrorHandling(async ({ routineId }) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.getRoutineById(String(routineId));
      if (!data || !data.routine) {
        return createEmptyResponse(`Routine with ID ${routineId} not found`);
      }
      const routine = formatRoutine(data.routine);
      return createJsonResponse(routine);
    }, "get-routine")
  );
  server.tool(
    "create-routine",
    "Create a new workout routine in your Hevy account. Requires a title and at least one exercise with sets. Optionally assign to a folder. Returns the full routine details including the new routine ID.",
    {
      title: z2.string().min(1),
      folderId: z2.coerce.number().nullable().optional(),
      notes: z2.string().optional(),
      exercises: z2.array(
        z2.object({
          exerciseTemplateId: z2.string().min(1),
          supersetId: z2.coerce.number().nullable().optional(),
          restSeconds: z2.coerce.number().int().min(0).optional(),
          notes: z2.string().optional(),
          sets: z2.array(
            z2.object({
              type: z2.enum(["warmup", "normal", "failure", "dropset"]).default("normal"),
              weightKg: z2.coerce.number().optional(),
              reps: z2.coerce.number().int().optional(),
              distanceMeters: z2.coerce.number().int().optional(),
              durationSeconds: z2.coerce.number().int().optional(),
              customMetric: z2.coerce.number().optional()
            })
          )
        })
      )
    },
    withErrorHandling(async (args) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const { title, folderId, notes, exercises } = args;
      const data = await hevyClient.createRoutine({
        routine: {
          title,
          folder_id: folderId ?? null,
          notes: notes ?? "",
          exercises: exercises.map(
            (exercise) => ({
              exercise_template_id: exercise.exerciseTemplateId,
              superset_id: exercise.supersetId ?? null,
              rest_seconds: exercise.restSeconds ?? null,
              notes: exercise.notes ?? null,
              sets: exercise.sets.map(
                (set) => ({
                  type: set.type,
                  weight_kg: set.weightKg ?? null,
                  reps: set.reps ?? null,
                  distance_meters: set.distanceMeters ?? null,
                  duration_seconds: set.durationSeconds ?? null,
                  custom_metric: set.customMetric ?? null
                })
              )
            })
          )
        }
      });
      if (!data) {
        return createEmptyResponse(
          "Failed to create routine: Server returned no data"
        );
      }
      const routine = formatRoutine(data);
      return createJsonResponse(routine, {
        pretty: true,
        indent: 2
      });
    }, "create-routine")
  );
  server.tool(
    "update-routine",
    "Update an existing routine by ID. You can modify the title, notes, and exercise configurations. Returns the updated routine with all changes applied.",
    {
      routineId: z2.string().min(1),
      title: z2.string().min(1),
      notes: z2.string().optional(),
      exercises: z2.array(
        z2.object({
          exerciseTemplateId: z2.string().min(1),
          supersetId: z2.coerce.number().nullable().optional(),
          restSeconds: z2.coerce.number().int().min(0).optional(),
          notes: z2.string().optional(),
          sets: z2.array(
            z2.object({
              type: z2.enum(["warmup", "normal", "failure", "dropset"]).default("normal"),
              weightKg: z2.coerce.number().optional(),
              reps: z2.coerce.number().int().optional(),
              distanceMeters: z2.coerce.number().int().optional(),
              durationSeconds: z2.coerce.number().int().optional(),
              customMetric: z2.coerce.number().optional()
            })
          )
        })
      )
    },
    withErrorHandling(async (args) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const { routineId, title, notes, exercises } = args;
      const data = await hevyClient.updateRoutine(routineId, {
        routine: {
          title,
          notes: notes ?? null,
          exercises: exercises.map(
            (exercise) => ({
              exercise_template_id: exercise.exerciseTemplateId,
              superset_id: exercise.supersetId ?? null,
              rest_seconds: exercise.restSeconds ?? null,
              notes: exercise.notes ?? null,
              sets: exercise.sets.map(
                (set) => ({
                  type: set.type,
                  weight_kg: set.weightKg ?? null,
                  reps: set.reps ?? null,
                  distance_meters: set.distanceMeters ?? null,
                  duration_seconds: set.durationSeconds ?? null,
                  custom_metric: set.customMetric ?? null
                })
              )
            })
          )
        }
      });
      if (!data) {
        return createEmptyResponse(
          `Failed to update routine with ID ${routineId}`
        );
      }
      const routine = formatRoutine(data);
      return createJsonResponse(routine, {
        pretty: true,
        indent: 2
      });
    }, "update-routine")
  );
}

// src/tools/templates.ts
import { z as z3 } from "zod";
function registerTemplateTools(server, hevyClient) {
  server.tool(
    "get-exercise-templates",
    "Get a paginated list of exercise templates (default and custom) with details like name, category, equipment, and muscle groups. Useful for browsing or searching available exercises.",
    {
      page: z3.coerce.number().int().gte(1).default(1),
      pageSize: z3.coerce.number().int().gte(1).lte(100).default(5)
    },
    withErrorHandling(
      async ({ page, pageSize }) => {
        if (!hevyClient) {
          throw new Error(
            "API client not initialized. Please provide HEVY_API_KEY."
          );
        }
        const data = await hevyClient.getExerciseTemplates({
          page,
          pageSize
        });
        const templates = data?.exercise_templates?.map(
          (template) => formatExerciseTemplate(template)
        ) || [];
        if (templates.length === 0) {
          return createEmptyResponse(
            "No exercise templates found for the specified parameters"
          );
        }
        return createJsonResponse(templates);
      },
      "get-exercise-templates"
    )
  );
  server.tool(
    "get-exercise-template",
    "Get complete details of a specific exercise template by its ID, including name, category, equipment, muscle groups, and notes.",
    {
      exerciseTemplateId: z3.string().min(1)
    },
    withErrorHandling(
      async ({ exerciseTemplateId }) => {
        if (!hevyClient) {
          throw new Error(
            "API client not initialized. Please provide HEVY_API_KEY."
          );
        }
        const data = await hevyClient.getExerciseTemplate(exerciseTemplateId);
        if (!data) {
          return createEmptyResponse(
            `Exercise template with ID ${exerciseTemplateId} not found`
          );
        }
        const template = formatExerciseTemplate(data);
        return createJsonResponse(template);
      },
      "get-exercise-template"
    )
  );
}

// src/tools/webhooks.ts
import { z as z40 } from "zod";

// src/generated/client/schemas/deletedWorkoutSchema.ts
import { z as z4 } from "zod";
var deletedWorkoutSchema = z4.object({
  "type": z4.string().describe("Indicates the type of the event (deleted)"),
  "id": z4.string().describe("The unique identifier of the deleted workout"),
  "deleted_at": z4.optional(z4.string().describe("A date string indicating when the workout was deleted"))
});

// src/generated/client/schemas/deleteV1WebhookSubscriptionSchema.ts
import { z as z5 } from "zod";
var deleteV1WebhookSubscriptionHeaderParamsSchema = z5.object({
  "api-key": z5.string().uuid().describe("Your API key")
});
var deleteV1WebhookSubscription200Schema = z5.any();

// src/generated/client/schemas/exerciseTemplateSchema.ts
import { z as z6 } from "zod";
var exerciseTemplateSchema = z6.object({
  "id": z6.optional(z6.string().describe("The exercise template ID.")),
  "title": z6.optional(z6.string().describe("The exercise title.")),
  "type": z6.optional(z6.string().describe("The exercise type.")),
  "primary_muscle_group": z6.optional(z6.string().describe("The primary muscle group of the exercise.")),
  "secondary_muscle_groups": z6.optional(z6.array(z6.string()).describe("The secondary muscle groups of the exercise.")),
  "is_custom": z6.optional(z6.boolean().describe("A boolean indicating whether the exercise is a custom exercise."))
});

// src/generated/client/schemas/getV1ExerciseTemplatesExercisetemplateidSchema.ts
import { z as z7 } from "zod";
var getV1ExerciseTemplatesExercisetemplateidPathParamsSchema = z7.object({
  "exerciseTemplateId": z7.any()
});
var getV1ExerciseTemplatesExercisetemplateidHeaderParamsSchema = z7.object({
  "api-key": z7.string().uuid()
});
var getV1ExerciseTemplatesExercisetemplateid404Schema = z7.any();

// src/generated/client/schemas/getV1ExerciseTemplatesSchema.ts
import { z as z8 } from "zod";
var getV1ExerciseTemplatesQueryParamsSchema = z8.object({
  "page": z8.coerce.number().int().default(1).describe("Page number (Must be 1 or greater)"),
  "pageSize": z8.coerce.number().int().default(5).describe("Number of items on the requested page (Max 100)")
});
var getV1ExerciseTemplatesHeaderParamsSchema = z8.object({
  "api-key": z8.string().uuid()
});
var getV1ExerciseTemplates200Schema = z8.object({
  "page": z8.optional(z8.number().int().default(1).describe("Current page number")),
  "page_count": z8.optional(z8.number().int().default(5).describe("Total number of pages")),
  "exercise_templates": z8.optional(z8.array(z8.lazy(() => exerciseTemplateSchema)))
});
var getV1ExerciseTemplates400Schema = z8.any();

// src/generated/client/schemas/routineFolderSchema.ts
import { z as z9 } from "zod";
var routineFolderSchema = z9.object({
  "id": z9.optional(z9.number().describe("The routine folder ID.")),
  "index": z9.optional(z9.number().describe("The routine folder index. Describes the order of the folder in the list.")),
  "title": z9.optional(z9.string().describe("The routine folder title.")),
  "updated_at": z9.optional(z9.string().describe("ISO 8601 timestamp of when the folder was last updated.")),
  "created_at": z9.optional(z9.string().describe("ISO 8601 timestamp of when the folder was created."))
});

// src/generated/client/schemas/getV1RoutineFoldersFolderidSchema.ts
import { z as z10 } from "zod";
var getV1RoutineFoldersFolderidPathParamsSchema = z10.object({
  "folderId": z10.any()
});
var getV1RoutineFoldersFolderidHeaderParamsSchema = z10.object({
  "api-key": z10.string().uuid()
});
var getV1RoutineFoldersFolderid404Schema = z10.any();

// src/generated/client/schemas/getV1RoutineFoldersSchema.ts
import { z as z11 } from "zod";
var getV1RoutineFoldersQueryParamsSchema = z11.object({
  "page": z11.coerce.number().int().default(1).describe("Page number (Must be 1 or greater)"),
  "pageSize": z11.coerce.number().int().default(5).describe("Number of items on the requested page (Max 10)")
});
var getV1RoutineFoldersHeaderParamsSchema = z11.object({
  "api-key": z11.string().uuid()
});
var getV1RoutineFolders200Schema = z11.object({
  "page": z11.optional(z11.number().int().default(1).describe("Current page number")),
  "page_count": z11.optional(z11.number().int().default(5).describe("Total number of pages")),
  "routine_folders": z11.optional(z11.array(z11.lazy(() => routineFolderSchema)))
});
var getV1RoutineFolders400Schema = z11.any();

// src/generated/client/schemas/routineSchema.ts
import { z as z12 } from "zod";
var routineSchema = z12.object({
  "id": z12.optional(z12.string().describe("The routine ID.")),
  "title": z12.optional(z12.string().describe("The routine title.")),
  "folder_id": z12.number().describe("The routine folder ID.").nullish(),
  "updated_at": z12.optional(z12.string().describe("ISO 8601 timestamp of when the routine was last updated.")),
  "created_at": z12.optional(z12.string().describe("ISO 8601 timestamp of when the routine was created.")),
  "exercises": z12.optional(z12.array(z12.object({
    "index": z12.optional(z12.number().describe("Index indicating the order of the exercise in the routine.")),
    "title": z12.optional(z12.string().describe("Title of the exercise")),
    "rest_seconds": z12.optional(z12.string().describe("The rest time in seconds between sets of the exercise")),
    "notes": z12.optional(z12.string().describe("Routine notes on the exercise")),
    "exercise_template_id": z12.optional(z12.string().describe("The id of the exercise template. This can be used to fetch the exercise template.")),
    "supersets_id": z12.number().describe("The id of the superset that the exercise belongs to. A value of null indicates the exercise is not part of a superset.").nullish(),
    "sets": z12.optional(z12.array(z12.object({
      "index": z12.optional(z12.number().describe("Index indicating the order of the set in the routine.")),
      "type": z12.optional(z12.string().describe("The type of set. This can be one of 'normal', 'warmup', 'dropset', 'failure'")),
      "weight_kg": z12.number().describe("Weight lifted in kilograms.").nullish(),
      "reps": z12.number().describe("Number of reps logged for the set").nullish(),
      "rep_range": z12.object({
        "start": z12.number().describe("Starting rep count for the range").nullish(),
        "end": z12.number().describe("Ending rep count for the range").nullish()
      }).describe("Range of reps for the set, if applicable").nullish(),
      "distance_meters": z12.number().describe("Number of meters logged for the set").nullish(),
      "duration_seconds": z12.number().describe("Number of seconds logged for the set").nullish(),
      "rpe": z12.number().describe("RPE (Relative perceived exertion) value logged for the set").nullish(),
      "custom_metric": z12.number().describe("Custom metric logged for the set (Currently only used to log floors or steps for stair machine exercises)").nullish()
    })))
  })))
});

// src/generated/client/schemas/getV1RoutinesRoutineidSchema.ts
import { z as z13 } from "zod";
var getV1RoutinesRoutineidPathParamsSchema = z13.object({
  "routineId": z13.any()
});
var getV1RoutinesRoutineidHeaderParamsSchema = z13.object({
  "api-key": z13.string().uuid()
});
var getV1RoutinesRoutineid200Schema = z13.object({
  "routine": z13.optional(z13.lazy(() => routineSchema))
});
var getV1RoutinesRoutineid400Schema = z13.object({
  "error": z13.optional(z13.string().describe("Error message"))
});

// src/generated/client/schemas/getV1RoutinesSchema.ts
import { z as z14 } from "zod";
var getV1RoutinesQueryParamsSchema = z14.object({
  "page": z14.coerce.number().int().default(1).describe("Page number (Must be 1 or greater)"),
  "pageSize": z14.coerce.number().int().default(5).describe("Number of items on the requested page (Max 10)")
});
var getV1RoutinesHeaderParamsSchema = z14.object({
  "api-key": z14.string().uuid()
});
var getV1Routines200Schema = z14.object({
  "page": z14.optional(z14.number().int().describe("Current page number")),
  "page_count": z14.optional(z14.number().int().describe("Total number of pages")),
  "routines": z14.optional(z14.array(z14.lazy(() => routineSchema)))
});
var getV1Routines400Schema = z14.any();

// src/generated/client/schemas/getV1WebhookSubscriptionSchema.ts
import { z as z15 } from "zod";
var getV1WebhookSubscriptionHeaderParamsSchema = z15.object({
  "api-key": z15.string().uuid().describe("Your API key")
});
var getV1WebhookSubscription200Schema = z15.object({
  "url": z15.optional(z15.string().describe("The webhook URL")),
  "auth_token": z15.optional(z15.string().describe("The auth token for the webhook"))
});
var getV1WebhookSubscription404Schema = z15.any();

// src/generated/client/schemas/getV1WorkoutsCountSchema.ts
import { z as z16 } from "zod";
var getV1WorkoutsCountHeaderParamsSchema = z16.object({
  "api-key": z16.string().uuid()
});
var getV1WorkoutsCount200Schema = z16.object({
  "workout_count": z16.optional(z16.number().int().default(42).describe("The total number of workouts"))
});

// src/generated/client/schemas/workoutSchema.ts
import { z as z17 } from "zod";
var workoutSchema = z17.object({
  "id": z17.optional(z17.string().describe("The workout ID.")),
  "title": z17.optional(z17.string().describe("The workout title.")),
  "description": z17.optional(z17.string().describe("The workout description.")),
  "start_time": z17.optional(z17.number().describe("ISO 8601 timestamp of when the workout was recorded to have started.")),
  "end_time": z17.optional(z17.number().describe("ISO 8601 timestamp of when the workout was recorded to have ended.")),
  "updated_at": z17.optional(z17.string().describe("ISO 8601 timestamp of when the workout was last updated.")),
  "created_at": z17.optional(z17.string().describe("ISO 8601 timestamp of when the workout was created.")),
  "exercises": z17.optional(z17.array(z17.object({
    "index": z17.optional(z17.number().describe("Index indicating the order of the exercise in the workout.")),
    "title": z17.optional(z17.string().describe("Title of the exercise")),
    "notes": z17.optional(z17.string().describe("Notes on the exercise")),
    "exercise_template_id": z17.optional(z17.string().describe("The id of the exercise template. This can be used to fetch the exercise template.")),
    "supersets_id": z17.number().describe("The id of the superset that the exercise belongs to. A value of null indicates the exercise is not part of a superset.").nullish(),
    "sets": z17.optional(z17.array(z17.object({
      "index": z17.optional(z17.number().describe("Index indicating the order of the set in the workout.")),
      "type": z17.optional(z17.string().describe("The type of set. This can be one of 'normal', 'warmup', 'dropset', 'failure'")),
      "weight_kg": z17.number().describe("Weight lifted in kilograms.").nullish(),
      "reps": z17.number().describe("Number of reps logged for the set").nullish(),
      "distance_meters": z17.number().describe("Number of meters logged for the set").nullish(),
      "duration_seconds": z17.number().describe("Number of seconds logged for the set").nullish(),
      "rpe": z17.number().describe("RPE (Relative perceived exertion) value logged for the set").nullish(),
      "custom_metric": z17.number().describe("Custom metric logged for the set (Currently only used to log floors or steps for stair machine exercises)").nullish()
    })))
  })))
});

// src/generated/client/schemas/updatedWorkoutSchema.ts
import { z as z18 } from "zod";
var updatedWorkoutSchema = z18.object({
  "type": z18.string().describe("Indicates the type of the event (updated)"),
  "workout": z18.lazy(() => workoutSchema)
});

// src/generated/client/schemas/paginatedWorkoutEventsSchema.ts
import { z as z19 } from "zod";
var paginatedWorkoutEventsSchema = z19.object({
  "page": z19.number().int().describe("The current page number"),
  "page_count": z19.number().int().describe("The total number of pages available"),
  "events": z19.array(z19.union([z19.lazy(() => updatedWorkoutSchema), z19.lazy(() => deletedWorkoutSchema)])).describe("An array of workout events (either updated or deleted)")
});

// src/generated/client/schemas/getV1WorkoutsEventsSchema.ts
import { z as z20 } from "zod";
var getV1WorkoutsEventsQueryParamsSchema = z20.object({
  "page": z20.coerce.number().int().default(1).describe("Page number (Must be 1 or greater)"),
  "pageSize": z20.coerce.number().int().default(5).describe("Number of items on the requested page (Max 10)"),
  "since": z20.string().default("1970-01-01T00:00:00Z")
});
var getV1WorkoutsEventsHeaderParamsSchema = z20.object({
  "api-key": z20.string().uuid()
});
var getV1WorkoutsEvents500Schema = z20.any();

// src/generated/client/schemas/getV1WorkoutsSchema.ts
import { z as z21 } from "zod";
var getV1WorkoutsQueryParamsSchema = z21.object({
  "page": z21.coerce.number().int().default(1).describe("Page number (Must be 1 or greater)"),
  "pageSize": z21.coerce.number().int().default(5).describe("Number of items on the requested page (Max 10)")
});
var getV1WorkoutsHeaderParamsSchema = z21.object({
  "api-key": z21.string().uuid()
});
var getV1Workouts200Schema = z21.object({
  "page": z21.optional(z21.number().int().describe("Current page number")),
  "page_count": z21.optional(z21.number().int().describe("Total number of pages")),
  "workouts": z21.optional(z21.array(z21.lazy(() => workoutSchema)))
});
var getV1Workouts400Schema = z21.any();

// src/generated/client/schemas/getV1WorkoutsWorkoutidSchema.ts
import { z as z22 } from "zod";
var getV1WorkoutsWorkoutidPathParamsSchema = z22.object({
  "workoutId": z22.any()
});
var getV1WorkoutsWorkoutidHeaderParamsSchema = z22.object({
  "api-key": z22.string().uuid()
});
var getV1WorkoutsWorkoutid404Schema = z22.any();

// src/generated/client/schemas/postRoutineFolderRequestBodySchema.ts
import { z as z23 } from "zod";
var postRoutineFolderRequestBodySchema = z23.object({
  "routine_folder": z23.optional(z23.object({
    "title": z23.optional(z23.string().describe("The title of the routine folder."))
  }))
});

// src/generated/client/schemas/postRoutinesRequestSetSchema.ts
import { z as z24 } from "zod";
var postRoutinesRequestSetSchema = z24.object({
  "type": z24.optional(z24.enum(["warmup", "normal", "failure", "dropset"]).describe("The type of the set.")),
  "weight_kg": z24.number().describe("The weight in kilograms.").nullish(),
  "reps": z24.number().int().describe("The number of repetitions.").nullish(),
  "distance_meters": z24.number().int().describe("The distance in meters.").nullish(),
  "duration_seconds": z24.number().int().describe("The duration in seconds.").nullish(),
  "custom_metric": z24.number().describe("A custom metric for the set. Currently used for steps and floors.").nullish(),
  "rep_range": z24.object({
    "start": z24.number().describe("Starting rep count for the range").nullish(),
    "end": z24.number().describe("Ending rep count for the range").nullish()
  }).describe("Range of reps for the set, if applicable").nullish()
});

// src/generated/client/schemas/postRoutinesRequestExerciseSchema.ts
import { z as z25 } from "zod";
var postRoutinesRequestExerciseSchema = z25.object({
  "exercise_template_id": z25.optional(z25.string().describe("The ID of the exercise template.")),
  "superset_id": z25.number().int().describe("The ID of the superset.").nullish(),
  "rest_seconds": z25.number().int().describe("The rest time in seconds.").nullish(),
  "notes": z25.string().describe("Additional notes for the exercise.").nullish(),
  "sets": z25.optional(z25.array(z25.lazy(() => postRoutinesRequestSetSchema)))
});

// src/generated/client/schemas/postRoutinesRequestBodySchema.ts
import { z as z26 } from "zod";
var postRoutinesRequestBodySchema = z26.object({
  "routine": z26.optional(z26.object({
    "title": z26.optional(z26.string().describe("The title of the routine.")),
    "folder_id": z26.number().describe('The folder id the routine should be added to. Pass null to insert the routine into default "My Routines" folder').nullish(),
    "notes": z26.optional(z26.string().describe("Additional notes for the routine.")),
    "exercises": z26.optional(z26.array(z26.lazy(() => postRoutinesRequestExerciseSchema)))
  }))
});

// src/generated/client/schemas/postV1RoutineFoldersSchema.ts
import { z as z27 } from "zod";
var postV1RoutineFoldersHeaderParamsSchema = z27.object({
  "api-key": z27.string().uuid()
});
var postV1RoutineFolders400Schema = z27.object({
  "error": z27.optional(z27.string().describe("Error message"))
});

// src/generated/client/schemas/postV1RoutinesSchema.ts
import { z as z28 } from "zod";
var postV1RoutinesHeaderParamsSchema = z28.object({
  "api-key": z28.string().uuid()
});
var postV1Routines400Schema = z28.object({
  "error": z28.optional(z28.string().describe("Error message"))
});
var postV1Routines403Schema = z28.object({
  "error": z28.optional(z28.string().describe("Error message"))
});

// src/generated/client/schemas/webhookRequestBodySchema.ts
import { z as z29 } from "zod";
var webhookRequestBodySchema = z29.object({
  "authToken": z29.optional(z29.string().describe("The auth token that will be send as Authorization header in the webhook.")),
  "url": z29.optional(z29.string().describe("The webhook URL."))
});

// src/generated/client/schemas/postV1WebhookSubscriptionSchema.ts
import { z as z30 } from "zod";
var postV1WebhookSubscriptionHeaderParamsSchema = z30.object({
  "api-key": z30.string().uuid()
});
var postV1WebhookSubscription201Schema = z30.any();
var postV1WebhookSubscription400Schema = z30.object({
  "error": z30.optional(z30.string().describe("Error message"))
});

// src/generated/client/schemas/postWorkoutsRequestSetSchema.ts
import { z as z31 } from "zod";
var postWorkoutsRequestSetSchema = z31.object({
  "type": z31.optional(z31.enum(["warmup", "normal", "failure", "dropset"]).describe("The type of the set.")),
  "weight_kg": z31.number().describe("The weight in kilograms.").nullish(),
  "reps": z31.number().int().describe("The number of repetitions.").nullish(),
  "distance_meters": z31.number().int().describe("The distance in meters.").nullish(),
  "duration_seconds": z31.number().int().describe("The duration in seconds.").nullish(),
  "custom_metric": z31.number().describe("A custom metric for the set. Currently used for steps and floors.").nullish(),
  "rpe": z31.union([z31.literal(6), z31.literal(7), z31.literal(7.5), z31.literal(8), z31.literal(8.5), z31.literal(9), z31.literal(9.5), z31.literal(10)]).describe("The Rating of Perceived Exertion (RPE).").nullish()
});

// src/generated/client/schemas/postWorkoutsRequestExerciseSchema.ts
import { z as z32 } from "zod";
var postWorkoutsRequestExerciseSchema = z32.object({
  "exercise_template_id": z32.optional(z32.string().describe("The ID of the exercise template.")),
  "superset_id": z32.number().int().describe("The ID of the superset.").nullish(),
  "notes": z32.string().describe("Additional notes for the exercise.").nullish(),
  "sets": z32.optional(z32.array(z32.lazy(() => postWorkoutsRequestSetSchema)))
});

// src/generated/client/schemas/postWorkoutsRequestBodySchema.ts
import { z as z33 } from "zod";
var postWorkoutsRequestBodySchema = z33.object({
  "workout": z33.optional(z33.object({
    "title": z33.optional(z33.string().describe("The title of the workout.")),
    "description": z33.string().describe("A description for the workout workout.").nullish(),
    "start_time": z33.optional(z33.string().describe("The time the workout started.")),
    "end_time": z33.optional(z33.string().describe("The time the workout ended.")),
    "is_private": z33.optional(z33.boolean().describe("A boolean indicating if the workout is private.")),
    "exercises": z33.optional(z33.array(z33.lazy(() => postWorkoutsRequestExerciseSchema)))
  }))
});

// src/generated/client/schemas/postV1WorkoutsSchema.ts
import { z as z34 } from "zod";
var postV1WorkoutsHeaderParamsSchema = z34.object({
  "api-key": z34.string().uuid()
});
var postV1Workouts400Schema = z34.object({
  "error": z34.optional(z34.string().describe("Error message"))
});

// src/generated/client/schemas/putRoutinesRequestSetSchema.ts
import { z as z35 } from "zod";
var putRoutinesRequestSetSchema = z35.object({
  "type": z35.optional(z35.enum(["warmup", "normal", "failure", "dropset"]).describe("The type of the set.")),
  "weight_kg": z35.number().describe("The weight in kilograms.").nullish(),
  "reps": z35.number().int().describe("The number of repetitions.").nullish(),
  "distance_meters": z35.number().int().describe("The distance in meters.").nullish(),
  "duration_seconds": z35.number().int().describe("The duration in seconds.").nullish(),
  "custom_metric": z35.number().describe("A custom metric for the set. Currently used for steps and floors.").nullish(),
  "rep_range": z35.object({
    "start": z35.number().describe("Starting rep count for the range").nullish(),
    "end": z35.number().describe("Ending rep count for the range").nullish()
  }).describe("Range of reps for the set, if applicable").nullish()
});

// src/generated/client/schemas/putRoutinesRequestExerciseSchema.ts
import { z as z36 } from "zod";
var putRoutinesRequestExerciseSchema = z36.object({
  "exercise_template_id": z36.optional(z36.string().describe("The ID of the exercise template.")),
  "superset_id": z36.number().int().describe("The ID of the superset.").nullish(),
  "rest_seconds": z36.number().int().describe("The rest time in seconds.").nullish(),
  "notes": z36.string().describe("Additional notes for the exercise.").nullish(),
  "sets": z36.optional(z36.array(z36.lazy(() => putRoutinesRequestSetSchema)))
});

// src/generated/client/schemas/putRoutinesRequestBodySchema.ts
import { z as z37 } from "zod";
var putRoutinesRequestBodySchema = z37.object({
  "routine": z37.optional(z37.object({
    "title": z37.optional(z37.string().describe("The title of the routine.")),
    "notes": z37.string().describe("Additional notes for the routine.").nullish(),
    "exercises": z37.optional(z37.array(z37.lazy(() => putRoutinesRequestExerciseSchema)))
  }))
});

// src/generated/client/schemas/putV1RoutinesRoutineidSchema.ts
import { z as z38 } from "zod";
var putV1RoutinesRoutineidPathParamsSchema = z38.object({
  "routineId": z38.any()
});
var putV1RoutinesRoutineidHeaderParamsSchema = z38.object({
  "api-key": z38.string().uuid()
});
var putV1RoutinesRoutineid400Schema = z38.object({
  "error": z38.optional(z38.string().describe("Error message"))
});
var putV1RoutinesRoutineid404Schema = z38.object({
  "error": z38.optional(z38.string().describe("Error message"))
});

// src/generated/client/schemas/putV1WorkoutsWorkoutidSchema.ts
import { z as z39 } from "zod";
var putV1WorkoutsWorkoutidPathParamsSchema = z39.object({
  "workoutId": z39.any()
});
var putV1WorkoutsWorkoutidHeaderParamsSchema = z39.object({
  "api-key": z39.string().uuid()
});
var putV1WorkoutsWorkoutid400Schema = z39.object({
  "error": z39.optional(z39.string().describe("Error message"))
});

// src/tools/webhooks.ts
var webhookUrlSchema = z40.string().url().refine(
  (url) => {
    try {
      const parsed = new URL(url);
      return parsed.protocol === "https:" || parsed.protocol === "http:";
    } catch {
      return false;
    }
  },
  {
    message: "Webhook URL must be a valid HTTP or HTTPS URL"
  }
).refine(
  (url) => {
    try {
      const parsed = new URL(url);
      return parsed.hostname !== "localhost" && !parsed.hostname.startsWith("127.");
    } catch {
      return false;
    }
  },
  {
    message: "Webhook URL cannot be localhost or loopback address"
  }
);
function registerWebhookTools(server, hevyClient) {
  server.tool(
    "get-webhook-subscription",
    "Get the current webhook subscription for this account. Returns the webhook URL and auth token if a subscription exists.",
    {},
    withErrorHandling(async () => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.getWebhookSubscription();
      if (!data) {
        return createEmptyResponse(
          "No webhook subscription found for this account"
        );
      }
      return createJsonResponse(data);
    }, "get-webhook-subscription")
  );
  server.tool(
    "create-webhook-subscription",
    "Create a new webhook subscription for this account. The webhook will receive POST requests when workouts are created. Your endpoint must respond with 200 OK within 5 seconds.",
    {
      url: webhookUrlSchema.describe(
        "The webhook URL that will receive POST requests when workouts are created"
      ),
      authToken: z40.string().optional().describe(
        "Optional auth token that will be sent as Authorization header in webhook requests"
      )
    },
    withErrorHandling(async ({ url, authToken }) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const requestBody = webhookRequestBodySchema.parse({
        url,
        authToken
      });
      const data = await hevyClient.createWebhookSubscription(requestBody);
      if (!data) {
        return createEmptyResponse(
          "Failed to create webhook subscription - please check your URL and try again"
        );
      }
      return createJsonResponse(data);
    }, "create-webhook-subscription")
  );
  server.tool(
    "delete-webhook-subscription",
    "Delete the current webhook subscription for this account. This will stop all webhook notifications.",
    {},
    withErrorHandling(async () => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.deleteWebhookSubscription();
      if (!data) {
        return createEmptyResponse(
          "Failed to delete webhook subscription - no subscription may exist or there was a server error"
        );
      }
      return createJsonResponse(data);
    }, "delete-webhook-subscription")
  );
}

// src/tools/workouts.ts
import { z as z41 } from "zod";
function registerWorkoutTools(server, hevyClient) {
  server.tool(
    "get-workouts",
    "Get a paginated list of workouts. Returns workout details including title, description, start/end times, and exercises performed. Results are ordered from newest to oldest.",
    {
      page: z41.coerce.number().gte(1).default(1),
      pageSize: z41.coerce.number().int().gte(1).lte(10).default(5)
    },
    withErrorHandling(async ({ page, pageSize }) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.getWorkouts({
        page,
        pageSize
      });
      const workouts = data?.workouts?.map((workout) => formatWorkout(workout)) || [];
      if (workouts.length === 0) {
        return createEmptyResponse(
          "No workouts found for the specified parameters"
        );
      }
      return createJsonResponse(workouts);
    }, "get-workouts")
  );
  server.tool(
    "get-workout",
    "Get complete details of a specific workout by ID. Returns all workout information including title, description, start/end times, and detailed exercise data.",
    {
      workoutId: z41.string().min(1)
    },
    withErrorHandling(async ({ workoutId }) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.getWorkout(workoutId);
      if (!data) {
        return createEmptyResponse(`Workout with ID ${workoutId} not found`);
      }
      const workout = formatWorkout(data);
      return createJsonResponse(workout);
    }, "get-workout")
  );
  server.tool(
    "get-workout-count",
    "Get the total number of workouts on the account. Useful for pagination or statistics.",
    {},
    withErrorHandling(async () => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.getWorkoutCount();
      const count = data ? data.workoutCount || 0 : 0;
      return createJsonResponse({ count });
    }, "get-workout-count")
  );
  server.tool(
    "get-workout-events",
    "Retrieve a paged list of workout events (updates or deletes) since a given date. Events are ordered from newest to oldest. The intention is to allow clients to keep their local cache of workouts up to date without having to fetch the entire list of workouts.",
    {
      page: z41.coerce.number().int().gte(1).default(1),
      pageSize: z41.coerce.number().int().gte(1).lte(10).default(5),
      since: z41.string().default("1970-01-01T00:00:00Z")
    },
    withErrorHandling(async ({ page, pageSize, since }) => {
      if (!hevyClient) {
        throw new Error(
          "API client not initialized. Please provide HEVY_API_KEY."
        );
      }
      const data = await hevyClient.getWorkoutEvents({
        page,
        pageSize,
        since
      });
      const events = data?.events || [];
      if (events.length === 0) {
        return createEmptyResponse(
          `No workout events found for the specified parameters since ${since}`
        );
      }
      return createJsonResponse(events);
    }, "get-workout-events")
  );
  server.tool(
    "create-workout",
    "Create a new workout in your Hevy account. Requires title, start/end times, and at least one exercise with sets. Returns the complete workout details upon successful creation including the newly assigned workout ID.",
    {
      title: z41.string().min(1),
      description: z41.string().optional().nullable(),
      startTime: z41.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
      endTime: z41.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
      isPrivate: z41.boolean().default(false),
      exercises: z41.array(
        z41.object({
          exerciseTemplateId: z41.string().min(1),
          supersetId: z41.coerce.number().nullable().optional(),
          notes: z41.string().optional().nullable(),
          sets: z41.array(
            z41.object({
              type: z41.enum(["warmup", "normal", "failure", "dropset"]).default("normal"),
              weightKg: z41.coerce.number().optional().nullable(),
              reps: z41.coerce.number().int().optional().nullable(),
              distanceMeters: z41.coerce.number().int().optional().nullable(),
              durationSeconds: z41.coerce.number().int().optional().nullable(),
              rpe: z41.coerce.number().optional().nullable(),
              customMetric: z41.coerce.number().optional().nullable()
            })
          )
        })
      )
    },
    withErrorHandling(
      async ({
        title,
        description,
        startTime,
        endTime,
        isPrivate,
        exercises
      }) => {
        if (!hevyClient) {
          throw new Error(
            "API client not initialized. Please provide HEVY_API_KEY."
          );
        }
        const requestBody = {
          workout: {
            title,
            description: description || null,
            startTime,
            endTime,
            isPrivate,
            exercises: exercises.map((exercise) => ({
              exerciseTemplateId: exercise.exerciseTemplateId,
              supersetId: exercise.supersetId || null,
              notes: exercise.notes || null,
              sets: exercise.sets.map((set) => ({
                type: set.type,
                weightKg: set.weightKg || null,
                reps: set.reps || null,
                distanceMeters: set.distanceMeters || null,
                durationSeconds: set.durationSeconds || null,
                rpe: set.rpe || null,
                customMetric: set.customMetric || null
              }))
            }))
          }
        };
        const data = await hevyClient.createWorkout(requestBody);
        if (!data) {
          return createEmptyResponse(
            "Failed to create workout: Server returned no data"
          );
        }
        const workout = formatWorkout(data);
        return createJsonResponse(workout, {
          pretty: true,
          indent: 2
        });
      },
      "create-workout"
    )
  );
  server.tool(
    "update-workout",
    "Update an existing workout by ID. You can modify the title, description, start/end times, privacy setting, and exercise data. Returns the updated workout with all changes applied.",
    {
      workoutId: z41.string().min(1),
      title: z41.string().min(1),
      description: z41.string().optional().nullable(),
      startTime: z41.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
      endTime: z41.string().regex(/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/),
      isPrivate: z41.boolean().default(false),
      exercises: z41.array(
        z41.object({
          exerciseTemplateId: z41.string().min(1),
          supersetId: z41.coerce.number().nullable().optional(),
          notes: z41.string().optional().nullable(),
          sets: z41.array(
            z41.object({
              type: z41.enum(["warmup", "normal", "failure", "dropset"]).default("normal"),
              weightKg: z41.coerce.number().optional().nullable(),
              reps: z41.coerce.number().int().optional().nullable(),
              distanceMeters: z41.coerce.number().int().optional().nullable(),
              durationSeconds: z41.coerce.number().int().optional().nullable(),
              rpe: z41.coerce.number().optional().nullable(),
              customMetric: z41.coerce.number().optional().nullable()
            })
          )
        })
      )
    },
    withErrorHandling(
      async ({
        workoutId,
        title,
        description,
        startTime,
        endTime,
        isPrivate,
        exercises
      }) => {
        const requestBody = {
          workout: {
            title,
            description: description || null,
            startTime,
            endTime,
            isPrivate,
            exercises: exercises.map((exercise) => ({
              exerciseTemplateId: exercise.exerciseTemplateId,
              supersetId: exercise.supersetId || null,
              notes: exercise.notes || null,
              sets: exercise.sets.map((set) => ({
                type: set.type,
                weightKg: set.weightKg || null,
                reps: set.reps || null,
                distanceMeters: set.distanceMeters || null,
                durationSeconds: set.durationSeconds || null,
                rpe: set.rpe || null,
                customMetric: set.customMetric || null
              }))
            }))
          }
        };
        const data = await hevyClient.updateWorkout(workoutId, requestBody);
        if (!data) {
          return createEmptyResponse(
            `Failed to update workout with ID ${workoutId}`
          );
        }
        const workout = formatWorkout(data);
        return createJsonResponse(workout, {
          pretty: true,
          indent: 2
        });
      },
      "update-workout-operation"
    )
  );
}

// src/utils/config.ts
function parseConfig(argv, env) {
  let apiKey = "";
  const apiKeyArgPatterns = [
    /^--hevy-api-key=(.+)$/i,
    /^--hevyApiKey=(.+)$/i,
    /^hevy-api-key=(.+)$/i
  ];
  for (const raw of argv) {
    for (const pattern of apiKeyArgPatterns) {
      const m = raw.match(pattern);
      if (m) {
        apiKey = m[1];
        break;
      }
    }
    if (apiKey) break;
  }
  if (!apiKey) {
    apiKey = env.HEVY_API_KEY || "";
  }
  return {
    apiKey
  };
}
function assertApiKey(apiKey) {
  if (!apiKey) {
    console.error(
      "Hevy API key is required. Provide it via the HEVY_API_KEY environment variable or the --hevy-api-key=YOUR_KEY command argument."
    );
    process.exit(1);
  }
}

// src/utils/hevyClientKubb.ts
import axios from "axios";

// src/generated/client/api/deleteV1WebhookSubscription.ts
import fetch from "@kubb/plugin-client/clients/axios";
function getDeleteV1WebhookSubscriptionUrl() {
  const res = { method: "DELETE", url: `/v1/webhook-subscription` };
  return res;
}
async function deleteV1WebhookSubscription(headers, config = {}) {
  const { client: request = fetch, ...requestConfig } = config;
  const res = await request({ method: "DELETE", url: getDeleteV1WebhookSubscriptionUrl().url.toString(), ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1ExerciseTemplates.ts
import fetch2 from "@kubb/plugin-client/clients/axios";
function getGetV1ExerciseTemplatesUrl() {
  const res = { method: "GET", url: `/v1/exercise_templates` };
  return res;
}
async function getV1ExerciseTemplates(headers, params, config = {}) {
  const { client: request = fetch2, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1ExerciseTemplatesUrl().url.toString(), params, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1ExerciseTemplatesExercisetemplateid.ts
import fetch3 from "@kubb/plugin-client/clients/axios";
function getGetV1ExerciseTemplatesExercisetemplateidUrl(exerciseTemplateId) {
  const res = { method: "GET", url: `/v1/exercise_templates/${exerciseTemplateId}` };
  return res;
}
async function getV1ExerciseTemplatesExercisetemplateid(exerciseTemplateId, headers, config = {}) {
  const { client: request = fetch3, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1ExerciseTemplatesExercisetemplateidUrl(exerciseTemplateId).url.toString(), ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1RoutineFolders.ts
import fetch4 from "@kubb/plugin-client/clients/axios";
function getGetV1RoutineFoldersUrl() {
  const res = { method: "GET", url: `/v1/routine_folders` };
  return res;
}
async function getV1RoutineFolders(headers, params, config = {}) {
  const { client: request = fetch4, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1RoutineFoldersUrl().url.toString(), params, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1RoutineFoldersFolderid.ts
import fetch5 from "@kubb/plugin-client/clients/axios";
function getGetV1RoutineFoldersFolderidUrl(folderId) {
  const res = { method: "GET", url: `/v1/routine_folders/${folderId}` };
  return res;
}
async function getV1RoutineFoldersFolderid(folderId, headers, config = {}) {
  const { client: request = fetch5, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1RoutineFoldersFolderidUrl(folderId).url.toString(), ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1Routines.ts
import fetch6 from "@kubb/plugin-client/clients/axios";
function getGetV1RoutinesUrl() {
  const res = { method: "GET", url: `/v1/routines` };
  return res;
}
async function getV1Routines(headers, params, config = {}) {
  const { client: request = fetch6, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1RoutinesUrl().url.toString(), params, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1RoutinesRoutineid.ts
import fetch7 from "@kubb/plugin-client/clients/axios";
function getGetV1RoutinesRoutineidUrl(routineId) {
  const res = { method: "GET", url: `/v1/routines/${routineId}` };
  return res;
}
async function getV1RoutinesRoutineid(routineId, headers, config = {}) {
  const { client: request = fetch7, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1RoutinesRoutineidUrl(routineId).url.toString(), ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1WebhookSubscription.ts
import fetch8 from "@kubb/plugin-client/clients/axios";
function getGetV1WebhookSubscriptionUrl() {
  const res = { method: "GET", url: `/v1/webhook-subscription` };
  return res;
}
async function getV1WebhookSubscription(headers, config = {}) {
  const { client: request = fetch8, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1WebhookSubscriptionUrl().url.toString(), ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1Workouts.ts
import fetch9 from "@kubb/plugin-client/clients/axios";
function getGetV1WorkoutsUrl() {
  const res = { method: "GET", url: `/v1/workouts` };
  return res;
}
async function getV1Workouts(headers, params, config = {}) {
  const { client: request = fetch9, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1WorkoutsUrl().url.toString(), params, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1WorkoutsCount.ts
import fetch10 from "@kubb/plugin-client/clients/axios";
function getGetV1WorkoutsCountUrl() {
  const res = { method: "GET", url: `/v1/workouts/count` };
  return res;
}
async function getV1WorkoutsCount(headers, config = {}) {
  const { client: request = fetch10, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1WorkoutsCountUrl().url.toString(), ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1WorkoutsEvents.ts
import fetch11 from "@kubb/plugin-client/clients/axios";
function getGetV1WorkoutsEventsUrl() {
  const res = { method: "GET", url: `/v1/workouts/events` };
  return res;
}
async function getV1WorkoutsEvents(headers, params, config = {}) {
  const { client: request = fetch11, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1WorkoutsEventsUrl().url.toString(), params, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/getV1WorkoutsWorkoutid.ts
import fetch12 from "@kubb/plugin-client/clients/axios";
function getGetV1WorkoutsWorkoutidUrl(workoutId) {
  const res = { method: "GET", url: `/v1/workouts/${workoutId}` };
  return res;
}
async function getV1WorkoutsWorkoutid(workoutId, headers, config = {}) {
  const { client: request = fetch12, ...requestConfig } = config;
  const res = await request({ method: "GET", url: getGetV1WorkoutsWorkoutidUrl(workoutId).url.toString(), ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/postV1RoutineFolders.ts
import fetch13 from "@kubb/plugin-client/clients/axios";
function getPostV1RoutineFoldersUrl() {
  const res = { method: "POST", url: `/v1/routine_folders` };
  return res;
}
async function postV1RoutineFolders(headers, data, config = {}) {
  const { client: request = fetch13, ...requestConfig } = config;
  const requestData = data;
  const res = await request({ method: "POST", url: getPostV1RoutineFoldersUrl().url.toString(), data: requestData, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/postV1Routines.ts
import fetch14 from "@kubb/plugin-client/clients/axios";
function getPostV1RoutinesUrl() {
  const res = { method: "POST", url: `/v1/routines` };
  return res;
}
async function postV1Routines(headers, data, config = {}) {
  const { client: request = fetch14, ...requestConfig } = config;
  const requestData = data;
  const res = await request({ method: "POST", url: getPostV1RoutinesUrl().url.toString(), data: requestData, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/postV1WebhookSubscription.ts
import fetch15 from "@kubb/plugin-client/clients/axios";
function getPostV1WebhookSubscriptionUrl() {
  const res = { method: "POST", url: `/v1/webhook-subscription` };
  return res;
}
async function postV1WebhookSubscription(headers, data, config = {}) {
  const { client: request = fetch15, ...requestConfig } = config;
  const requestData = data;
  const res = await request({ method: "POST", url: getPostV1WebhookSubscriptionUrl().url.toString(), data: requestData, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/postV1Workouts.ts
import fetch16 from "@kubb/plugin-client/clients/axios";
function getPostV1WorkoutsUrl() {
  const res = { method: "POST", url: `/v1/workouts` };
  return res;
}
async function postV1Workouts(headers, data, config = {}) {
  const { client: request = fetch16, ...requestConfig } = config;
  const requestData = data;
  const res = await request({ method: "POST", url: getPostV1WorkoutsUrl().url.toString(), data: requestData, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/putV1RoutinesRoutineid.ts
import fetch17 from "@kubb/plugin-client/clients/axios";
function getPutV1RoutinesRoutineidUrl(routineId) {
  const res = { method: "PUT", url: `/v1/routines/${routineId}` };
  return res;
}
async function putV1RoutinesRoutineid(routineId, headers, data, config = {}) {
  const { client: request = fetch17, ...requestConfig } = config;
  const requestData = data;
  const res = await request({ method: "PUT", url: getPutV1RoutinesRoutineidUrl(routineId).url.toString(), data: requestData, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/generated/client/api/putV1WorkoutsWorkoutid.ts
import fetch18 from "@kubb/plugin-client/clients/axios";
function getPutV1WorkoutsWorkoutidUrl(workoutId) {
  const res = { method: "PUT", url: `/v1/workouts/${workoutId}` };
  return res;
}
async function putV1WorkoutsWorkoutid(workoutId, headers, data, config = {}) {
  const { client: request = fetch18, ...requestConfig } = config;
  const requestData = data;
  const res = await request({ method: "PUT", url: getPutV1WorkoutsWorkoutidUrl(workoutId).url.toString(), data: requestData, ...requestConfig, headers: { ...headers, ...requestConfig.headers } });
  return res.data;
}

// src/utils/hevyClientKubb.ts
function createClient(apiKey, baseUrl = "https://api.hevyapp.com") {
  const axiosInstance = axios.create({
    baseURL: baseUrl,
    headers: {
      "api-key": apiKey
    }
  });
  const headers = {
    "api-key": apiKey
  };
  const client = axiosInstance;
  return {
    // Workouts
    getWorkouts: (params) => getV1Workouts(headers, params, { client }),
    getWorkout: (workoutId) => getV1WorkoutsWorkoutid(workoutId, headers, { client }),
    createWorkout: (data) => postV1Workouts(headers, data, { client }),
    updateWorkout: (workoutId, data) => putV1WorkoutsWorkoutid(workoutId, headers, data, {
      client
    }),
    getWorkoutCount: () => getV1WorkoutsCount(headers, { client }),
    getWorkoutEvents: (params) => getV1WorkoutsEvents(headers, params, { client }),
    // Routines
    getRoutines: (params) => getV1Routines(headers, params, { client }),
    getRoutineById: (routineId) => getV1RoutinesRoutineid(routineId, headers, { client }),
    createRoutine: (data) => postV1Routines(headers, data, { client }),
    updateRoutine: (routineId, data) => putV1RoutinesRoutineid(routineId, headers, data, {
      client
    }),
    // Exercise Templates
    getExerciseTemplates: (params) => getV1ExerciseTemplates(headers, params, { client }),
    getExerciseTemplate: (templateId) => getV1ExerciseTemplatesExercisetemplateid(templateId, headers, {
      client
    }),
    // Routine Folders
    getRoutineFolders: (params) => getV1RoutineFolders(headers, params, { client }),
    createRoutineFolder: (data) => postV1RoutineFolders(headers, data, { client }),
    getRoutineFolder: (folderId) => getV1RoutineFoldersFolderid(folderId, headers, {
      client
    }),
    // Webhooks
    getWebhookSubscription: () => getV1WebhookSubscription(headers, { client }),
    createWebhookSubscription: (data) => postV1WebhookSubscription(headers, data, { client }),
    deleteWebhookSubscription: () => deleteV1WebhookSubscription(headers, { client })
  };
}

// src/utils/hevyClient.ts
function createClient2(apiKey, baseUrl) {
  return createClient(apiKey, baseUrl);
}

// src/index.ts
var HEVY_API_BASEURL = "https://api.hevyapp.com";
var serverConfigSchema = z42.object({
  apiKey: z42.string().min(1, "Hevy API key is required").describe("Your Hevy API key (available in the Hevy app settings).")
});
var configSchema = serverConfigSchema;
function buildServer(apiKey) {
  const server = new McpServer({
    name,
    version
  });
  const hevyClient = createClient2(apiKey, HEVY_API_BASEURL);
  registerWorkoutTools(server, hevyClient);
  registerRoutineTools(server, hevyClient);
  registerTemplateTools(server, hevyClient);
  registerFolderTools(server, hevyClient);
  registerWebhookTools(server, hevyClient);
  return server;
}
function createServer({ config }) {
  const { apiKey } = serverConfigSchema.parse(config);
  const server = buildServer(apiKey);
  return server.server;
}
async function runServer() {
  const args = process.argv.slice(2);
  const cfg = parseConfig(args, process.env);
  const apiKey = cfg.apiKey;
  assertApiKey(apiKey);
  const server = buildServer(apiKey);
  const transport = new StdioServerTransport();
  await server.connect(transport);
}
var isDirectExecution = (() => {
  if (typeof process === "undefined" || !Array.isArray(process.argv)) {
    return false;
  }
  if (typeof import.meta === "undefined" || !import.meta?.url) {
    return false;
  }
  try {
    const modulePath = fileURLToPath(import.meta.url);
    return process.argv[1] === modulePath;
  } catch {
    return false;
  }
})();
if (isDirectExecution) {
  runServer().catch((error) => {
    console.error("Fatal error in main():", error);
    process.exit(1);
  });
}
export {
  configSchema,
  createServer as default
};
//# sourceMappingURL=index.js.map