/*
 * Duplicate File Detector using OS System Calls
 *
 * Operating Systems Project
 *
 * Features:
 * 1. Recursively scans a directory
 * 2. Finds regular files
 * 3. Compares file sizes
 * 4. Calculates a hash using file contents
 * 5. Reports duplicate files
 *
 * System calls / POSIX functions used:
 * open(), read(), close(), stat(), opendir(), readdir(), closedir()
 */
#define _POSIX_C_SOURCE 200809L
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/stat.h>
#include <dirent.h>
#include <limits.h>
#include <errno.h>

#define BUFFER_SIZE 4096

/* Structure to store information about each file */
typedef struct
{
    char path[PATH_MAX];
    off_t size;
    unsigned long hash;
} FileInfo;

/* Dynamic array of files */
FileInfo *files = NULL;
size_t file_count = 0;
size_t file_capacity = 0;

/*
 * Simple FNV-1a hash.
 * This is used only to identify possible duplicate files.
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
        perror("open");
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

    if (bytes_read == -1)
    {
        perror("read");
        close(fd);
        return 0;
    }

    close(fd);

    return hash;
}

/*
 * Add a file to the dynamic array.
 */
void add_file(const char *path, off_t size, unsigned long hash)
{
    if (file_count >= file_capacity)
    {
        size_t new_capacity;

        if (file_capacity == 0)
            new_capacity = 10;
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
 * Recursively scan a directory.
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

        /* Ignore . and .. */
        if (strcmp(entry->d_name, ".") == 0 ||
            strcmp(entry->d_name, "..") == 0)
        {
            continue;
        }

        /*
         * Construct complete path.
         */
        int result = snprintf(
            path,
            sizeof(path),
            "%s/%s",
            directory,
            entry->d_name
        );

        if (result < 0 || result >= (int)sizeof(path))
        {
            fprintf(stderr, "Path too long: %s\n", entry->d_name);
            continue;
        }

        /*
         * Get file information using stat().
         */
        if (stat(path, &file_stat) == -1)
        {
            perror(path);
            continue;
        }

        /*
         * If directory, recursively scan it.
         */
        if (S_ISDIR(file_stat.st_mode))
        {
            scan_directory(path);
        }

        /*
         * If regular file, process it.
         */
        else if (S_ISREG(file_stat.st_mode))
        {
            unsigned long hash;

            printf("Scanning: %s\n", path);

            /*
             * First check the file size.
             * Then calculate the hash.
             */
            hash = calculate_hash(path);

            if (hash != 0)
            {
                add_file(path, file_stat.st_size, hash);
            }
        }
    }

    closedir(dir);
}

/*
 * Display duplicate files.
 */
void find_duplicates(void)
{
    int found = 0;

    printf("\n========================================\n");
    printf("           DUPLICATE FILES\n");
    printf("========================================\n");

    for (size_t i = 0; i < file_count; i++)
    {
        int duplicate_group = 0;

        for (size_t j = i + 1; j < file_count; j++)
        {
            /*
             * Files are considered duplicates when:
             *
             * 1. Their sizes are equal
             * 2. Their hashes are equal
             */
            if (files[i].size == files[j].size &&
                files[i].hash == files[j].hash)
            {
                if (!duplicate_group)
                {
                    printf("\nDuplicate Group:\n");
                    printf("  %s\n", files[i].path);
                    duplicate_group = 1;
                }

                printf("  %s\n", files[j].path);
                found = 1;
            }
        }
    }

    if (!found)
    {
        printf("\nNo duplicate files found.\n");
    }

    printf("\n========================================\n");
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
    if (argc != 2)
    {
        printf("Usage: %s <directory>\n", argv[0]);
        printf("\nExample:\n");
        printf("  %s ./testdata\n", argv[0]);
        return EXIT_FAILURE;
    }

    printf("========================================\n");
    printf("      DUPLICATE FILE DETECTOR\n");
    printf("========================================\n");

    printf("\nDirectory: %s\n\n", argv[1]);

    /*
     * Start recursive scanning.
     */
    scan_directory(argv[1]);

    printf("\nTotal files scanned: %zu\n", file_count);

    /*
     * Compare files and display duplicates.
     */
    find_duplicates();

    cleanup();

    return EXIT_SUCCESS;
}
