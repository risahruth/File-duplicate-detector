#define _POSIX_C_SOURCE 200809L

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>
#include <limits.h>

#define BUFFER_SIZE 4096

#ifndef PATH_MAX
#define PATH_MAX 4096
#endif

typedef struct
{
    char path[PATH_MAX];
    off_t size;
    unsigned long hash;
} FileInfo;

FileInfo *files = NULL;
size_t file_count = 0;
size_t file_capacity = 0;


/*
 * Calculate FNV-1a hash using open(), read() and close().
 */
unsigned long calculate_hash(const char *filepath)
{
    int fd;
    char buffer[BUFFER_SIZE];
    ssize_t bytes_read;

    unsigned long hash = 2166136261u;

    fd = open(filepath, O_RDONLY);

    if (fd == -1)
    {
        return 0;
    }

    while ((bytes_read = read(fd, buffer, BUFFER_SIZE)) > 0)
    {
        for (ssize_t i = 0; i < bytes_read; i++)
        {
            hash ^= (unsigned char)buffer[i];
            hash *= 16777619u;
        }
    }

    close(fd);

    if (bytes_read == -1)
    {
        return 0;
    }

    return hash;
}


/*
 * Add file information to dynamic array.
 */
void add_file(const char *path, off_t size, unsigned long hash)
{
    if (file_count >= file_capacity)
    {
        size_t new_capacity;

        if (file_capacity == 0)
            new_capacity = 50;
        else
            new_capacity = file_capacity * 2;

        FileInfo *temp = realloc(
            files,
            new_capacity * sizeof(FileInfo)
        );

        if (temp == NULL)
        {
            perror("realloc");
            exit(EXIT_FAILURE);
        }

        files = temp;
        file_capacity = new_capacity;
    }

    strncpy(files[file_count].path, path, PATH_MAX - 1);
    files[file_count].path[PATH_MAX - 1] = '\0';

    files[file_count].size = size;
    files[file_count].hash = hash;

    file_count++;
}


/*
 * Recursively scan directories.
 */
void scan_directory(const char *directory)
{
    DIR *dir;
    struct dirent *entry;

    dir = opendir(directory);

    if (dir == NULL)
    {
        perror(directory);
        return;
    }

    while ((entry = readdir(dir)) != NULL)
    {
        char path[PATH_MAX];
        struct stat file_stat;

        if (strcmp(entry->d_name, ".") == 0 ||
            strcmp(entry->d_name, "..") == 0)
        {
            continue;
        }

        int result = snprintf(
            path,
            sizeof(path),
            "%s/%s",
            directory,
            entry->d_name
        );

        if (result < 0 || result >= (int)sizeof(path))
        {
            continue;
        }

        if (stat(path, &file_stat) == -1)
        {
            continue;
        }

        if (S_ISDIR(file_stat.st_mode))
        {
            scan_directory(path);
        }
        else if (S_ISREG(file_stat.st_mode))
        {
            unsigned long hash;

            hash = calculate_hash(path);

            if (hash != 0)
            {
                add_file(
                    path,
                    file_stat.st_size,
                    hash
                );
            }
        }
    }

    closedir(dir);
}


/*
 * Convert bytes into a human-readable size.
 */
void format_size(off_t bytes, char *output, size_t output_size)
{
    double size = (double)bytes;

    if (size >= 1024 * 1024 * 1024)
    {
        snprintf(
            output,
            output_size,
            "%.2f GB",
            size / (1024 * 1024 * 1024)
        );
    }
    else if (size >= 1024 * 1024)
    {
        snprintf(
            output,
            output_size,
            "%.2f MB",
            size / (1024 * 1024)
        );
    }
    else if (size >= 1024)
    {
        snprintf(
            output,
            output_size,
            "%.2f KB",
            size / 1024
        );
    }
    else
    {
        snprintf(
            output,
            output_size,
            "%ld B",
            (long)bytes
        );
    }
}


/*
 * Generate duplicate information.
 *
 * Results are written to results.txt so that the GUI can read them.
 */
void find_duplicates(const char *result_file)
{
    FILE *output;

    size_t duplicate_groups = 0;
    size_t duplicate_files = 0;
    off_t potential_savings = 0;

    output = fopen(result_file, "w");

    if (output == NULL)
    {
        perror("fopen");
        return;
    }

    fprintf(output, "DUPLICATE_FILE_DETECTOR\n");
    fprintf(output, "FILES_SCANNED=%zu\n", file_count);

    for (size_t i = 0; i < file_count; i++)
    {
        int group_found = 0;

        for (size_t j = i + 1; j < file_count; j++)
        {
            if (files[i].size == files[j].size &&
                files[i].hash == files[j].hash)
            {
                if (!group_found)
                {
                    char size_string[50];

                    format_size(
                        files[i].size,
                        size_string,
                        sizeof(size_string)
                    );

                    fprintf(
                        output,
                        "\nGROUP\n"
                    );

                    fprintf(
                        output,
                        "SIZE=%ld\n",
                        (long)files[i].size
                    );

                    fprintf(
                        output,
                        "SIZE_HUMAN=%s\n",
                        size_string
                    );

                    fprintf(
                        output,
                        "FILE=%s\n",
                        files[i].path
                    );

                    group_found = 1;

                    duplicate_groups++;
                    duplicate_files++;
                }

                fprintf(
                    output,
                    "FILE=%s\n",
                    files[j].path
                );

                duplicate_files++;

                potential_savings += files[j].size;
            }
        }
    }

    fprintf(
        output,
        "\nSUMMARY\n"
    );

    fprintf(
        output,
        "DUPLICATE_GROUPS=%zu\n",
        duplicate_groups
    );

    fprintf(
        output,
        "DUPLICATE_FILES=%zu\n",
        duplicate_files
    );

    fprintf(
        output,
        "POTENTIAL_SAVINGS=%ld\n",
        (long)potential_savings
    );

    fclose(output);

    /*
     * Human-readable terminal summary.
     */
    printf("\n========================================\n");
    printf("       DUPLICATE FILE DETECTOR\n");
    printf("========================================\n");

    printf("Files scanned       : %zu\n", file_count);
    printf("Duplicate groups    : %zu\n", duplicate_groups);
    printf("Duplicate files     : %zu\n", duplicate_files);

    char savings[50];

    format_size(
        potential_savings,
        savings,
        sizeof(savings)
    );

    printf("Potential space     : %s\n", savings);

    printf("Results saved to    : %s\n", result_file);

    printf("========================================\n");
}


/*
 * Free allocated memory.
 */
void cleanup(void)
{
    free(files);
}


/*
 * Main function.
 */
int main(int argc, char *argv[])
{
    const char *result_file = "results.txt";

    if (argc != 2)
    {
        printf("Usage: %s <directory>\n", argv[0]);
        printf("\nExample:\n");
        printf("  %s testdata\n", argv[0]);

        return EXIT_FAILURE;
    }

    printf("Scanning directory: %s\n", argv[1]);

    scan_directory(argv[1]);

    find_duplicates(result_file);

    cleanup();

    return EXIT_SUCCESS;
}